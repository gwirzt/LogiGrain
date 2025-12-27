from fastapi import FastAPI, HTTPException
from Arca.wsaa import ArcaSettings, get_arca_access_ticket
import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
from typing import Dict, Any

# Importar routers de cada sector
from Playa_Camiones.routes import router as playa_router
from Porteria_Ingreso.routes import router as ingreso_router  
from Porteria_Egreso.routes import router as egreso_router
from Calada.routes import router as calada_router
from Balanzas.routes import router as balanzas_router

# Cargar variables de entorno
load_dotenv()

# Logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configurar handler si no existe
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

app = FastAPI(
    title="LogiGrain - Terminal Portuaria",
    description="Sistema integral de gestión para terminal portuaria con integración ARCA/AFIP",
    version="1.0.0"
)

# Registrar routers de cada sector
app.include_router(playa_router)
app.include_router(ingreso_router)
app.include_router(egreso_router) 
app.include_router(calada_router)
app.include_router(balanzas_router)

# Obtener ruta base del proyecto
BASE_DIR = Path(__file__).parent.absolute()

@app.get("/")
async def root():
    """Endpoint raíz con información del sistema."""
    return {
        "sistema": "LogiGrain - Terminal Portuaria",
        "version": "1.0.0",
        "descripcion": "Sistema integral de gestión para terminal portuaria",
        "sectores_operativos": [
            {
                "id": 1,
                "nombre": "Playa de Camiones",
                "endpoint": "/playa-camiones",
                "descripcion": "Recepción, validación ARCA, facturación"
            },
            {
                "id": 3,
                "nombre": "Portería Ingreso", 
                "endpoint": "/porteria-ingreso",
                "descripcion": "Control de acceso, verificación documental"
            },
            {
                "id": 5,
                "nombre": "Calada",
                "endpoint": "/calada", 
                "descripcion": "Inspección, análisis calidad, clasificación"
            },
            {
                "id": 7-9,
                "nombre": "Balanzas",
                "endpoint": "/balanzas",
                "descripcion": "Registro pesos bruto/tara, cálculo neto"
            },
            {
                "id": 10,
                "nombre": "Portería Egreso",
                "endpoint": "/porteria-egreso",
                "descripcion": "Control egreso, cierre carta porte"
            }
        ],
        "servicios_arca": [
            "/get-ticket - Token ARCA (CPE por defecto)",
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


@app.get("/get-ticket")
async def get_arca_access_ticket_endpoint():
    """
    Obtiene el Access Ticket de ARCA/AFIP (CPE por defecto).
    
    Servicio: Cartas de Porte Electrónica
    Utiliza configuración desde .env sin parámetros requeridos.
    """
    logger.info("Iniciando solicitud de Access Ticket ARCA - CPE")
    
    try:
        # Ejecutar flujo completo sin parámetros (usa .env automáticamente)
        result = get_arca_access_ticket()
        
        if result['success']:
            logger.info("Access Ticket ARCA obtenido exitosamente")
            return {
                "status": "success",
                "message": "Access Ticket obtenido correctamente de ARCA/AFIP",
                "data": {
                    "token": result['token'],
                    "sign": result['sign'],
                    "service": result['service'],
                    "service_type": result['service_type'],
                    "environment": result['environment'],
                    "timestamp": result['timestamp'],
                    "valid_for": "24 horas desde generación"
                }
            }
        else:
            logger.error(f"Error en autenticación ARCA: {result['error']}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "error": result['error'],
                    "details": result['details'],
                    "suggestion": "Verificar certificados SSL y conectividad con AFIP"
                }
            )
            
    except Exception as e:
        logger.error(f"Error inesperado en endpoint /get-ticket: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error inesperado en autenticación ARCA: {str(e)}",
                "details": "Error interno del servidor",
                "suggestion": "Contactar al administrador del sistema"
            }
        )


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