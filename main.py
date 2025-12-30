from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import SQLModel, create_engine, Session, select
from jose import JWTError, jwt
from datetime import datetime, timedelta
from Arca.wsaa import ArcaSettings, get_arca_access_ticket
import os
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
from typing import Dict, Any, Optional

# Modelos de datos
from Modelos.usuario import (
    Usuario, Puerto, UsuarioPuerto, 
    UsuarioLogin, LoginResponse, UsuarioResponse, PuertoResponse
)
from Modelos.arca_tokens import (
    ArcaToken, ArcaTokenRequest, ArcaTokenResponse
)

# Cargar variables de entorno
load_dotenv()

# Logging centralizado
from utils.logger import setup_logger
logger = setup_logger('main')

# Configuración de base de datos SQLite
DATABASE_URL = "sqlite:///./logigrain.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Crear base de datos y tablas si no existen"""
    try:
        SQLModel.metadata.create_all(engine, checkfirst=True)
    except Exception as e:
        logger.warning(f"Las tablas ya existen o hay un problema menor: {e}")

def get_session():
    """Dependency para obtener sesión de base de datos"""
    with Session(engine) as session:
        yield session

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "logigrain-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        is_admin: bool = payload.get("is_admin")
        puertos: list = payload.get("puertos")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
            
        return {
            "username": username,
            "user_id": user_id,
            "is_admin": is_admin,
            "puertos": puertos
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

def get_current_user(session: Session = Depends(get_session), token_data: dict = Depends(verify_token)):
    """Obtener usuario actual desde el token JWT"""
    statement = select(Usuario).where(Usuario.id == token_data["user_id"])
    usuario = session.exec(statement).first()
    
    if not usuario:
        logger.error(f"Usuario no encontrado en BD: ID {token_data['user_id']}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    if not usuario.habilitado:
        logger.warning(f"Usuario deshabilitado: {usuario.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario deshabilitado"
        )
    
    return usuario

def log_endpoint_access(action: str, usuario: Usuario, puerto_codigo: str = None, success: bool = True, details: str = None):
    """Registrar acceso a endpoints con información completa"""
    status_msg = "ÉXITO" if success else "FRACASO"
    puerto_info = f", Puerto: {puerto_codigo}" if puerto_codigo else ""
    detail_info = f", Detalles: {details}" if details else ""
    
    logger.info(f"ENDPOINT ACCESS - Usuario: {usuario.username} (ID: {usuario.id}){puerto_info}, Acción: {action}, Estado: {status_msg}{detail_info}")

# === FUNCIONES DE CACHE ARCA === #

def get_cached_arca_token(usuario_id: int, puerto_codigo: str, servicio_tipo: str, session: Session) -> Optional[ArcaToken]:
    """
    Buscar token ARCA válido en cache.
    
    Args:
        usuario_id: ID del usuario
        puerto_codigo: Código del puerto (ej: TRP1)  
        servicio_tipo: Tipo de servicio (CPE, EMBARQUES, FACTURACION)
        session: Sesión de base de datos
        
    Returns:
        ArcaToken si existe y es válido, None en caso contrario
    """
    try:
        statement = select(ArcaToken).where(
            ArcaToken.usuario_id == usuario_id,
            ArcaToken.puerto_codigo == puerto_codigo,
            ArcaToken.servicio_tipo == servicio_tipo,
            ArcaToken.fecha_vencimiento > datetime.utcnow()
        ).order_by(ArcaToken.fecha_solicitud.desc())
        
        token = session.exec(statement).first()
        
        if token and not token.is_expired():
            logger.info(f"Token ARCA encontrado en cache - Usuario: {usuario_id}, Puerto: {puerto_codigo}, Servicio: {servicio_tipo}, Vence: {token.fecha_vencimiento}")
            return token
        elif token and token.is_expired():
            logger.info(f"Token ARCA expirado encontrado - Eliminando del cache")
            session.delete(token)
            session.commit()
            
        return None
        
    except Exception as e:
        logger.error(f"Error al buscar token ARCA en cache: {str(e)}")
        return None

def save_arca_token_to_cache(usuario_id: int, puerto_codigo: str, servicio_tipo: str, 
                           token: str, sign: str, wsaa_url: str, servicio_nombre: str, 
                           session: Session) -> ArcaToken:
    """
    Guardar nuevo token ARCA en cache.
    
    Args:
        usuario_id: ID del usuario
        puerto_codigo: Código del puerto
        servicio_tipo: Tipo de servicio
        token: Token XML de ARCA
        sign: Sign de autenticación
        wsaa_url: URL del servicio WSAA
        servicio_nombre: Nombre del servicio
        session: Sesión de base de datos
        
    Returns:
        ArcaToken guardado
    """
    try:
        # Eliminar tokens anteriores del mismo usuario/puerto/servicio
        statement = select(ArcaToken).where(
            ArcaToken.usuario_id == usuario_id,
            ArcaToken.puerto_codigo == puerto_codigo,
            ArcaToken.servicio_tipo == servicio_tipo
        )
        tokens_anteriores = session.exec(statement).all()
        
        for token_anterior in tokens_anteriores:
            session.delete(token_anterior)
        
        # Crear nuevo token
        nuevo_token = ArcaToken(
            usuario_id=usuario_id,
            puerto_codigo=puerto_codigo,
            servicio_tipo=servicio_tipo,
            token=token,
            sign=sign,
            wsaa_url=wsaa_url,
            servicio_nombre=servicio_nombre
        )
        
        session.add(nuevo_token)
        session.commit()
        session.refresh(nuevo_token)
        
        logger.info(f"Token ARCA guardado en cache - Usuario: {usuario_id}, Puerto: {puerto_codigo}, Servicio: {servicio_tipo}, Vence: {nuevo_token.fecha_vencimiento}")
        
        return nuevo_token
        
    except Exception as e:
        logger.error(f"Error al guardar token ARCA en cache: {str(e)}")
        session.rollback()
        raise

def validate_user_puerto_access(usuario: Usuario, puerto_codigo: str, session: Session) -> bool:
    """
    Validar que el usuario tenga acceso al puerto especificado.
    
    Args:
        usuario: Usuario autenticado
        puerto_codigo: Código del puerto a validar
        session: Sesión de base de datos
        
    Returns:
        bool: True si tiene acceso, False en caso contrario
    """
    try:
        statement = select(UsuarioPuerto, Puerto).join(Puerto).where(
            UsuarioPuerto.usuario_id == usuario.id,
            Puerto.codigo == puerto_codigo,
            UsuarioPuerto.habilitado == True,
            Puerto.habilitado == True
        )
        
        resultado = session.exec(statement).first()
        return resultado is not None
        
    except Exception as e:
        logger.error(f"Error al validar acceso a puerto: {str(e)}")
        return False

app = FastAPI(
    title="LogiGrain - Terminal Portuaria",
    description="Sistema integral de gestión para terminal portuaria con integración ARCA/AFIP",
    version="1.0.0"
)

# Crear tablas al iniciar
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("Base de datos y tablas creadas")

# Obtener ruta base del proyecto
BASE_DIR = Path(__file__).parent.absolute()

# === ENDPOINTS DE AUTENTICACIÓN === #

@app.post("/login", response_model=LoginResponse)
async def login(
    user_credentials: UsuarioLogin, 
    session: Session = Depends(get_session)
):
    """
    Endpoint de login con JSON en body.
    Retorna token JWT y lista de puertos del usuario.
    """
    logger.info(f"Intento de login para usuario: {user_credentials.username}")
    
    try:
        # Buscar usuario por username
        statement = select(Usuario).where(Usuario.username == user_credentials.username)
        usuario = session.exec(statement).first()
        
        if not usuario:
            logger.warning(f"Usuario no encontrado: {user_credentials.username}")
            raise HTTPException(
                status_code=401, 
                detail="Credenciales inválidas"
            )
        
        # Verificar contraseña
        if not usuario.verify_password(user_credentials.password):
            logger.warning(f"Contraseña incorrecta para usuario: {user_credentials.username}")
            raise HTTPException(
                status_code=401,
                detail="Credenciales inválidas"
            )
        
        # Verificar que el usuario esté habilitado
        if not usuario.habilitado:
            logger.warning(f"Usuario deshabilitado: {user_credentials.username}")
            raise HTTPException(
                status_code=403,
                detail="Usuario deshabilitado"
            )
        
        # Obtener puertos del usuario
        statement_puertos = select(UsuarioPuerto, Puerto).join(Puerto).where(
            UsuarioPuerto.usuario_id == usuario.id,
            UsuarioPuerto.habilitado == True,
            Puerto.habilitado == True
        )
        resultados = session.exec(statement_puertos).all()
        
        if not resultados:
            logger.warning(f"Usuario sin puertos asignados: {user_credentials.username}")
            raise HTTPException(
                status_code=403,
                detail="Usuario sin puertos asignados"
            )
        
        # Construir lista de puertos
        puertos = [
            PuertoResponse(
                id=puerto.id,
                nombre=puerto.nombre,
                codigo=puerto.codigo,
                descripcion=puerto.descripcion,
                ubicacion=puerto.ubicacion,
                habilitado=puerto.habilitado
            ) for _, puerto in resultados
        ]
        
        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.utcnow()
        session.add(usuario)
        session.commit()
        
        # Crear token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": usuario.username,
            "user_id": usuario.id,
            "is_admin": usuario.es_admin,
            "puertos": [p.codigo for p in puertos]
        }
        access_token = create_access_token(
            data=token_data, 
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login exitoso para usuario: {user_credentials.username}")
        
        return LoginResponse(
            usuario=UsuarioResponse(
                id=usuario.id,
                username=usuario.username,
                nombre_completo=usuario.nombre_completo,
                email=usuario.email,
                habilitado=usuario.habilitado,
                es_admin=usuario.es_admin,
                fecha_creacion=usuario.fecha_creacion,
                ultimo_acceso=usuario.ultimo_acceso
            ),
            puertos=puertos,
            token=access_token,
            mensaje=f"Login exitoso. Acceso a {len(puertos)} puerto(s)."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

# === ENDPOINTS PRINCIPALES === #

@app.get("/")
async def root():
    """Endpoint raíz con información del sistema."""
    return {
        "sistema": "LogiGrain - Terminal Portuaria",
        "version": "1.0.0",
        "descripcion": "Sistema integral de gestión para terminal portuaria",
        "estado": "Configuración base - Integración ARCA/AFIP activa",
        "sectores_operativos": "En desarrollo - Estructura por definir",
        "servicios_arca": [
            "/get-ticket-cpe - Token Cartas de Porte Electrónica", 
            "/get-ticket-embarques - Token Comunicaciones de Embarques",
            "/get-ticket-facturacion - Token Facturación Electrónica"
        ],
        "diagnosticos": [
            "/health - Verificación de salud",
            "/diagnose-certs - Diagnóstico certificados SSL",
            "/docs - Documentación Swagger"
        ]
    }


@app.post("/get-ticket-cpe")
async def get_ticket_cpe(
    request: ArcaTokenRequest, 
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtiene Access Ticket específico para Cartas de Porte Electrónica."""
    puerto_codigo = request.puerto_codigo
    log_endpoint_access("Solicitud Token CPE", current_user, puerto_codigo)
    
    try:
        # Validar acceso del usuario al puerto
        if not validate_user_puerto_access(current_user, puerto_codigo, session):
            log_endpoint_access("Token CPE - Acceso Denegado", current_user, puerto_codigo, success=False, details="Usuario sin acceso al puerto")
            raise HTTPException(
                status_code=403, 
                detail=f"Usuario no tiene acceso al puerto {puerto_codigo}"
            )
        
        # Buscar token en cache
        cached_token = get_cached_arca_token(current_user.id, puerto_codigo, "CPE", session)
        
        if cached_token:
            tiempo_restante = cached_token.tiempo_restante()
            cache_info = {
                "from_cache": True,
                "fecha_solicitud": cached_token.fecha_solicitud.isoformat(),
                "fecha_vencimiento": cached_token.fecha_vencimiento.isoformat(),
                "tiempo_restante_minutos": int(tiempo_restante.total_seconds() / 60)
            }
            
            response_data = {
                "success": True,
                "token": cached_token.token,
                "sign": cached_token.sign,
                "service": cached_token.servicio_nombre,
                "wsaa_url": cached_token.wsaa_url
            }
            
            log_endpoint_access("Token CPE - Cache Hit", current_user, puerto_codigo, success=True, 
                             details=f"Token reutilizado, vence en {int(tiempo_restante.total_seconds() / 60)} minutos")
            
            return ArcaTokenResponse(
                status="success",
                message="Token CPE obtenido desde cache",
                data=response_data,
                cache_info=cache_info
            )
        
        # Solicitar nuevo token a ARCA
        result = get_arca_access_ticket("CPE")
        
        if result['success']:
            # Guardar en cache
            nuevo_token = save_arca_token_to_cache(
                usuario_id=current_user.id,
                puerto_codigo=puerto_codigo,
                servicio_tipo="CPE",
                token=result['token'],
                sign=result['sign'],
                wsaa_url=result.get('wsaa_url', ''),
                servicio_nombre=result.get('service', 'wscpe'),
                session=session
            )
            
            cache_info = {
                "from_cache": False,
                "fecha_solicitud": nuevo_token.fecha_solicitud.isoformat(),
                "fecha_vencimiento": nuevo_token.fecha_vencimiento.isoformat(),
                "tiempo_restante_minutos": 480  # 8 horas
            }
            
            log_endpoint_access("Token CPE - Nuevo Solicitado", current_user, puerto_codigo, success=True, details="Token generado y guardado en cache")
            
            return ArcaTokenResponse(
                status="success",
                message="Token CPE obtenido y guardado en cache",
                data=result,
                cache_info=cache_info
            )
        else:
            log_endpoint_access("Token CPE Error", current_user, puerto_codigo, success=False, details=str(result))
            raise HTTPException(status_code=500, detail=result)
            
    except HTTPException:
        raise
    except Exception as e:
        log_endpoint_access("Token CPE Excepción", current_user, puerto_codigo, success=False, details=str(e))
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/get-ticket-embarques") 
async def get_ticket_embarques(
    request: ArcaTokenRequest,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtiene Access Ticket específico para Comunicaciones de Embarques."""
    puerto_codigo = request.puerto_codigo
    log_endpoint_access("Solicitud Token EMBARQUES", current_user, puerto_codigo)
    
    try:
        # Validar acceso del usuario al puerto
        if not validate_user_puerto_access(current_user, puerto_codigo, session):
            log_endpoint_access("Token EMBARQUES - Acceso Denegado", current_user, puerto_codigo, success=False, details="Usuario sin acceso al puerto")
            raise HTTPException(
                status_code=403, 
                detail=f"Usuario no tiene acceso al puerto {puerto_codigo}"
            )
        
        # Buscar token en cache
        cached_token = get_cached_arca_token(current_user.id, puerto_codigo, "EMBARQUES", session)
        
        if cached_token:
            tiempo_restante = cached_token.tiempo_restante()
            cache_info = {
                "from_cache": True,
                "fecha_solicitud": cached_token.fecha_solicitud.isoformat(),
                "fecha_vencimiento": cached_token.fecha_vencimiento.isoformat(),
                "tiempo_restante_minutos": int(tiempo_restante.total_seconds() / 60)
            }
            
            response_data = {
                "success": True,
                "token": cached_token.token,
                "sign": cached_token.sign,
                "service": cached_token.servicio_nombre,
                "wsaa_url": cached_token.wsaa_url
            }
            
            log_endpoint_access("Token EMBARQUES - Cache Hit", current_user, puerto_codigo, success=True, 
                             details=f"Token reutilizado, vence en {int(tiempo_restante.total_seconds() / 60)} minutos")
            
            return ArcaTokenResponse(
                status="success",
                message="Token EMBARQUES obtenido desde cache",
                data=response_data,
                cache_info=cache_info
            )
        
        # Solicitar nuevo token a ARCA
        result = get_arca_access_ticket("EMBARQUES")
        
        if result['success']:
            # Guardar en cache
            nuevo_token = save_arca_token_to_cache(
                usuario_id=current_user.id,
                puerto_codigo=puerto_codigo,
                servicio_tipo="EMBARQUES",
                token=result['token'],
                sign=result['sign'],
                wsaa_url=result.get('wsaa_url', ''),
                servicio_nombre=result.get('service', 'wconscomunicacionembarque'),
                session=session
            )
            
            cache_info = {
                "from_cache": False,
                "fecha_solicitud": nuevo_token.fecha_solicitud.isoformat(),
                "fecha_vencimiento": nuevo_token.fecha_vencimiento.isoformat(),
                "tiempo_restante_minutos": 480  # 8 horas
            }
            
            log_endpoint_access("Token EMBARQUES - Nuevo Solicitado", current_user, puerto_codigo, success=True, details="Token generado y guardado en cache")
            
            return ArcaTokenResponse(
                status="success",
                message="Token EMBARQUES obtenido y guardado en cache",
                data=result,
                cache_info=cache_info
            )
        else:
            log_endpoint_access("Token EMBARQUES Error", current_user, puerto_codigo, success=False, details=str(result))
            raise HTTPException(status_code=500, detail=result)
            
    except HTTPException:
        raise
    except Exception as e:
        log_endpoint_access("Token EMBARQUES Excepción", current_user, puerto_codigo, success=False, details=str(e))
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/get-ticket-facturacion")
async def get_ticket_facturacion(
    request: ArcaTokenRequest,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtiene Access Ticket específico para Facturación Electrónica."""
    puerto_codigo = request.puerto_codigo
    log_endpoint_access("Solicitud Token FACTURACIÓN", current_user, puerto_codigo)
    
    try:
        # Validar acceso del usuario al puerto
        if not validate_user_puerto_access(current_user, puerto_codigo, session):
            log_endpoint_access("Token FACTURACIÓN - Acceso Denegado", current_user, puerto_codigo, success=False, details="Usuario sin acceso al puerto")
            raise HTTPException(
                status_code=403, 
                detail=f"Usuario no tiene acceso al puerto {puerto_codigo}"
            )
        
        # Buscar token en cache
        cached_token = get_cached_arca_token(current_user.id, puerto_codigo, "FACTURACION", session)
        
        if cached_token:
            tiempo_restante = cached_token.tiempo_restante()
            cache_info = {
                "from_cache": True,
                "fecha_solicitud": cached_token.fecha_solicitud.isoformat(),
                "fecha_vencimiento": cached_token.fecha_vencimiento.isoformat(),
                "tiempo_restante_minutos": int(tiempo_restante.total_seconds() / 60)
            }
            
            response_data = {
                "success": True,
                "token": cached_token.token,
                "sign": cached_token.sign,
                "service": cached_token.servicio_nombre,
                "wsaa_url": cached_token.wsaa_url
            }
            
            log_endpoint_access("Token FACTURACIÓN - Cache Hit", current_user, puerto_codigo, success=True, 
                             details=f"Token reutilizado, vence en {int(tiempo_restante.total_seconds() / 60)} minutos")
            
            return ArcaTokenResponse(
                status="success",
                message="Token FACTURACIÓN obtenido desde cache",
                data=response_data,
                cache_info=cache_info
            )
        
        # Solicitar nuevo token a ARCA
        result = get_arca_access_ticket("FACTURACION")
        
        if result['success']:
            # Guardar en cache
            nuevo_token = save_arca_token_to_cache(
                usuario_id=current_user.id,
                puerto_codigo=puerto_codigo,
                servicio_tipo="FACTURACION",
                token=result['token'],
                sign=result['sign'],
                wsaa_url=result.get('wsaa_url', ''),
                servicio_nombre=result.get('service', 'wsfe'),
                session=session
            )
            
            cache_info = {
                "from_cache": False,
                "fecha_solicitud": nuevo_token.fecha_solicitud.isoformat(),
                "fecha_vencimiento": nuevo_token.fecha_vencimiento.isoformat(),
                "tiempo_restante_minutos": 480  # 8 horas
            }
            
            log_endpoint_access("Token FACTURACIÓN - Nuevo Solicitado", current_user, puerto_codigo, success=True, details="Token generado y guardado en cache")
            
            return ArcaTokenResponse(
                status="success",
                message="Token FACTURACIÓN obtenido y guardado en cache",
                data=result,
                cache_info=cache_info
            )
        else:
            log_endpoint_access("Token FACTURACIÓN Error", current_user, puerto_codigo, success=False, details=str(result))
            raise HTTPException(status_code=500, detail=result)
            
    except HTTPException:
        raise
    except Exception as e:
        log_endpoint_access("Token FACTURACIÓN Excepción", current_user, puerto_codigo, success=False, details=str(e))
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.get("/health")
async def health_check(current_user: Usuario = Depends(get_current_user)):
    """Endpoint de verificación de salud del sistema."""
    log_endpoint_access("Health Check", current_user)
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user.username,
        "services": {
            "api": "running",
            "arca_integration": "configured",
            "database": "connected"
        }
    }


@app.get("/diagnose-certs")
async def diagnose_certificates(current_user: Usuario = Depends(get_current_user)):
    """
    Endpoint de diagnóstico para verificar el estado de los certificados SSL.
    Muestra configuración para todos los servicios desde .env
    """
    log_endpoint_access("Diagnóstico Certificados SSL", current_user)
    
    import os
    
    diagnostics = {
        "base_dir": str(BASE_DIR),
        "env_config": {
            "cert_base_dir": os.getenv('ARCA_CERT_BASE_DIR'),
            "environment": os.getenv('ARCA_ENVIRONMENT', 'PROD')
        },
        "services": {}
    }
    
    # Diagnosticar cada servicio
    services = ["CPE", "EMBARQUES", "FACTURACION"]
    
    for service in services:
        try:
            # Obtener configuración del servicio
            from Arca.wsaa import _get_service_config
            config = _get_service_config(service, "")
            
            service_diag = {
                "service_name": config.service_name,
                "cert_file": config.cert_file,
                "key_file": config.key_file,
                "wsaa_url": config.wsaa_url,
                "cert_exists": os.path.exists(config.cert_file),
                "key_exists": os.path.exists(config.key_file),
                "cert_size": os.path.getsize(config.cert_file) if os.path.exists(config.cert_file) else 0,
                "key_size": os.path.getsize(config.key_file) if os.path.exists(config.key_file) else 0
            }
            
            # Probar carga de certificados
            try:
                config.validate_certificates()
                service_diag["validation"] = "success"
            except Exception as e:
                service_diag["validation"] = f"error: {e}"
            
            diagnostics["services"][service] = service_diag
            
        except Exception as e:
            diagnostics["services"][service] = {"error": str(e)}
    
    return {
        "status": "diagnostics_complete",
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user.username,
        "diagnostics": diagnostics
    }


# Configuración multipuerto
def create_app_config() -> Dict[str, Any]:
    """
    Configuración para ejecutar la API en múltiples puertos.
    Permite operación simultánea en diferentes puertos para redundancia.
    """
    return {
        "primary_port": 8080,
        "secondary_port": 8081, 
        "host": "127.0.0.1",
        "reload": True,
        "log_level": "info"
    }


async def run_multiport_server():
    """
    Ejecuta el servidor en múltiples puertos simultáneamente.
    Configuración para alta disponibilidad y balanceo de carga.
    """
    config = create_app_config()
    
    logger.info(f"Iniciando LogiGrain en puertos {config['primary_port']} y {config['secondary_port']}")
    
    # TODO: Implementar ejecución real multipuerto con asyncio
    # Por ahora retorna configuración para uso manual
    return {
        "message": "Configuración multipuerto disponible",
        "puertos": [config['primary_port'], config['secondary_port']],
        "comando_primario": f"uvicorn main:app --host {config['host']} --port {config['primary_port']} --reload",
        "comando_secundario": f"uvicorn main:app --host {config['host']} --port {config['secondary_port']} --reload"
    }


@app.get("/system-info")
async def get_system_info(current_user: Usuario = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Información completa del sistema y configuración multipuerto.
    """
    log_endpoint_access("System Info", current_user)
    config = create_app_config()
    
    return {
        "sistema": "LogiGrain - Terminal Portuaria",
        "version": "1.0.0",
        "arquitectura": "Microservicios por sector",
        "usuario_actual": current_user.username,
        "puertos_acceso": [p.codigo for p in current_user.puertos] if hasattr(current_user, 'puertos') else [],
        "configuracion_multipuerto": await run_multiport_server(),
        "sectores_implementados": 5,
        "integracion_arca": "Activa - 3 servicios",
        "modelos_datos": "Centralizados en /Modelos",
        "estado": "Desarrollo - Estructura base implementada",
        "timestamp": datetime.utcnow().isoformat()
    }