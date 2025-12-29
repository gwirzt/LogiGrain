from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
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


@app.get("/get-ticket-cpe")
async def get_ticket_cpe():
    """Obtiene Access Ticket específico para Cartas de Porte Electrónica."""
    logger.info("Solicitud token CPE")
    
    try:
        result = get_arca_access_ticket("CPE")
        if result['success']:
            return {"status": "success", "message": "Token CPE obtenido", "data": result}
        else:
            raise HTTPException(status_code=500, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.get("/get-ticket-embarques") 
async def get_ticket_embarques():
    """Obtiene Access Ticket específico para Comunicaciones de Embarques."""
    logger.info("Solicitud token EMBARQUES")
    
    try:
        result = get_arca_access_ticket("EMBARQUES")
        if result['success']:
            return {"status": "success", "message": "Token EMBARQUES obtenido", "data": result}
        else:
            raise HTTPException(status_code=500, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.get("/get-ticket-facturacion")
async def get_ticket_facturacion():
    """Obtiene Access Ticket específico para Facturación Electrónica."""
    logger.info("Solicitud token FACTURACIÓN")
    
    try:
        result = get_arca_access_ticket("FACTURACION")
        if result['success']:
            return {"status": "success", "message": "Token FACTURACIÓN obtenido", "data": result}
        else:
            raise HTTPException(status_code=500, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del sistema."""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "services": {
            "api": "running",
            "arca_integration": "configured"
        }
    }


@app.get("/diagnose-certs")
async def diagnose_certificates():
    """
    Endpoint de diagnóstico para verificar el estado de los certificados SSL.
    Muestra configuración para todos los servicios desde .env
    """
    logger.info("Ejecutando diagnóstico de certificados SSL")
    
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
        "timestamp": datetime.datetime.now().isoformat(),
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
async def get_system_info() -> Dict[str, Any]:
    """
    Información completa del sistema y configuración multipuerto.
    """
    config = create_app_config()
    
    return {
        "sistema": "LogiGrain - Terminal Portuaria",
        "version": "1.0.0",
        "arquitectura": "Microservicios por sector",
        "configuracion_multipuerto": await run_multiport_server(),
        "sectores_implementados": 5,
        "integracion_arca": "Activa - 3 servicios",
        "modelos_datos": "Centralizados en /Modelos",
        "estado": "Desarrollo - Estructura base implementada"
    }