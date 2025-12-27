# Rutas FastAPI para Playa de Camiones
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import logging
from .wscpe_client import WSCPEClient
from .models import ConsultaCPERequest, ConsultaLoteCPERequest, XMLTemplateRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/playa-camiones", tags=["Playa de Camiones"])

# Instancia del cliente WSCPE
wscpe_client = WSCPEClient()

@router.get("/")
async def get_playa_status() -> Dict[str, Any]:
    """
    Estado actual de la playa de camiones.
    Monitorea camiones en espera, validación ARCA y facturación.
    """
    return {
        "sector": "Playa de Camiones",
        "sector_id": 1,
        "descripcion": "Recepción, validación ARCA, facturación",
        "distancia": "20km del puerto",
        "status": "operational",
        "capacidad_maxima": 500,
        "camiones_actuales": 0,
        "servicios": [
            "Validación Cartas de Porte Electrónicas",
            "Control documental ARCA/AFIP", 
            "Facturación electrónica",
            "Gestión de turnos y prioridades"
        ]
    }

@router.post("/validar-carta-porte")
async def validar_carta_porte(numero_carta: str) -> Dict[str, Any]:
    """
    Valida una carta de porte electrónica contra ARCA/AFIP.
    Integración con servicios CPE para verificación documental.
    """
    logger.info(f"Validando carta de porte: {numero_carta}")
    
    # TODO: Integrar con ARCA CPE para validación real
    return {
        "numero_carta": numero_carta,
        "status": "validado",
        "mensaje": "Carta de porte válida - integración ARCA pendiente",
        "sector": "playa_camiones"
    }

@router.get("/cola-espera")
async def get_cola_espera() -> Dict[str, Any]:
    """
    Obtiene la cola de camiones en espera en playa de camiones.
    Sistema FIFO por tipo de cereal.
    """
    return {
        "sector": "Playa de Camiones",
        "cola_actual": [],
        "tiempo_espera_promedio": "45 minutos",
        "organizacion": "FIFO por tipo de cereal",
        "capacidad_disponible": 500
    }


@router.post("/consultar-cpe")
async def consultar_carta_porte_electronica(request: ConsultaCPERequest) -> Dict[str, Any]:
    """
    Consulta una Carta de Porte Electrónica específica usando WSCPE.
    Utiliza el formato XML correcto con ConsultarCPEAutomotorReq.
    
    Request JSON:
    {
        "token": "TOKEN_ARCA_BASE64",
        "sign": "SIGN_ARCA",  
        "cuit_representada": "30606754538",
        "nro_ctg": "10226304603"
    }
    """
    
    logger.info(f"Consultando CTG {request.nro_ctg} para CUIT {request.cuit_representada}")
    
    try:
        # Usar el cliente WSCPE con formato correcto
        resultado = await wscpe_client.consultar_carta_porte(
            token=request.token,
            sign=request.sign,
            cuit_representada=request.cuit_representada,
            nro_ctg=request.nro_ctg
        )
        
        if resultado['success']:
            return {
                "status": "success",
                "message": f"CTG {request.nro_ctg} consultado exitosamente",
                "cpe_data": resultado['data'],
                "sector": "playa_camiones",
                "timestamp": resultado['timestamp']
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error consultando CTG",
                    "details": resultado['error'],
                    "nro_ctg": request.nro_ctg
                }
            )
            
    except Exception as e:
        logger.error(f"Error en consulta CTG {request.nro_ctg}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error interno consultando CTG: {str(e)}",
                "nro_ctg": request.nro_ctg,
                "suggestion": "Verificar token, sign y conectividad con WSCPE"
            }
        )


@router.post("/consultar-lote-cpes")
async def consultar_lote_cartas_porte(request: ConsultaLoteCPERequest) -> Dict[str, Any]:
    """
    Consulta múltiples CTGs en lote usando token y sign.
    Útil para procesar varios camiones simultáneamente.
    
    Request JSON:
    {
        "token": "TOKEN_ARCA_BASE64",
        "sign": "SIGN_ARCA",
        "cuit_representada": "30606754538", 
        "numeros_ctg": ["10226304603", "10226304604"]
    }
    """
    
    try:
        logger.info(f"Consultando lote de {len(request.numeros_ctg)} CTGs para CUIT {request.cuit_representada}")
        
        resultados = []
        
        for nro_ctg in request.numeros_ctg:
            resultado = await wscpe_client.consultar_carta_porte(
                token=request.token,
                sign=request.sign,
                cuit_representada=request.cuit_representada,
                nro_ctg=nro_ctg
            )
            resultados.append(resultado)
        
        return {
            "status": "success",
            "message": f"Lote de {len(request.numeros_ctg)} CTGs procesado",
            "cuit_representada": request.cuit_representada,
            "total_consultados": len(request.numeros_ctg),
            "resultados": resultados,
            "sector": "playa_camiones"
        }
        
    except Exception as e:
        logger.error(f"Error en consulta lote CTGs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error procesando lote de CTGs: {str(e)}",
                "suggestion": "Verificar formato de request y conectividad WSCPE"
            }
        )


@router.post("/xml-template")
async def get_xml_template(request: XMLTemplateRequest) -> Dict[str, Any]:
    """
    Genera el template XML que se enviará al webservice WSCPE.
    Útil para debugging y verificación del formato.
    
    Request JSON:
    {
        "cuit_representada": "30606754538",
        "nro_ctg": "10226304603"  
    }
    """
    
    try:
        # XML de ejemplo con placeholders
        xml_template = wscpe_client.create_cpe_query_xml(
            token="TOKEN_PLACEHOLDER",
            sign="SIGN_PLACEHOLDER",
            cuit_representada=request.cuit_representada,
            nro_ctg=request.nro_ctg
        )
        
        return {
            "status": "template_generated",
            "cuit_representada": request.cuit_representada,
            "nro_ctg": request.nro_ctg,
            "xml_template": xml_template,
            "webservice_url": wscpe_client.wscpe_url,
            "soap_action": "https://serviciosjava.afip.gob.ar/wscpe/ConsultarCPEAutomotor",
            "note": "Reemplazar TOKEN_PLACEHOLDER y SIGN_PLACEHOLDER con valores reales"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"Error generando template: {str(e)}"}
        )


@router.post("/consultar-cpe-directo")
async def consultar_cpe_con_token_obtenido(request: XMLTemplateRequest) -> Dict[str, Any]:
    """
    Consulta CTG usando tu token y sign ya obtenidos.
    Endpoint directo para probar con tus credenciales actuales.
    
    Request JSON:
    {
        "cuit_representada": "30606754538",
        "nro_ctg": "10226304603"
    }
    """
    
    # Tu token y sign obtenidos del endpoint /get-ticket-cpe (actualizados)
    token_actual = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+CiAgICA8aWQgc3JjPSJDTj13c2FhLCBPPUFGSVAsIEM9QVIsIFNFUklBTE5VTUJFUj1DVUlUIDMzNjkzNDUwMjM5IiB1bmlxdWVfaWQ9IjE1MTg3ODg0MzMiIGdlbl90aW1lPSIxNzU3MDA4MDc5IiBleHBfdGltZT0iMTc1NzA1MTMzOSIvPgogICAgPG9wZXJhdGlvbiB0eXBlPSJsb2dpbiIgdmFsdWU9ImdyYW50ZWQiPgogICAgICAgIDxsb2dpbiBlbnRpdHk9IjMzNjkzNDUwMjM5IiBzZXJ2aWNlPSJ3c2NwZSIgdWlkPSJTRVJJQUxOVU1CRVI9Q1VJVCAyMDE3MjQyMDkzMiwgQ049bmFjaW9uMTg0NiIgYXV0aG1ldGhvZD0iY21zIiByZWdtZXRob2Q9IjIyIj4KICAgICAgICAgICAgPHJlbGF0aW9ucz4KICAgICAgICAgICAgICAgIDxyZWxhdGlvbiBrZXk9IjMwNjA2NzU0NTM4IiByZWx0eXBlPSI0Ii8+CiAgICAgICAgICAgIDwvcmVsYXRpb25zPgogICAgICAgIDwvbG9naW4+CiAgICA8L29wZXJhdGlvbj4KPC9zc28+Cg=="
    sign_actual = "h7PGTYHiX74kLJP1hVx75wh3Qr6TcKlb9Q7zmzufaMya1JiYAZay2xi1fnYF3RhVAjw29mb2sqz4Pq+MeHA2ganXKbN4H0LVK6Xl8D4pkqxSrwk3bDvov/OCqctvT0ccDCZ3f4ERNg+7JKffPozuazAQb31DS8Ti6ZO303OXFao="
    
    logger.info(f"Consultando CTG {request.nro_ctg} con token actual")
    
    try:
        # Consultar con tu token actual
        resultado = await wscpe_client.consultar_carta_porte(
            token=token_actual,
            sign=sign_actual,
            cuit_representada=request.cuit_representada,
            nro_ctg=request.nro_ctg
        )
        
        return {
            "status": "success",
            "message": f"CTG {request.nro_ctg} consultado con token actual",
            "resultado": resultado,
            "token_info": {
                "service": "wscpe",
                "cuit_representada": request.cuit_representada,
                "generated": "Token del ejemplo proporcionado",
                "expires": "Verificar en token XML"
            }
        }
        
    except Exception as e:
        logger.error(f"Error consultando CTG {request.nro_ctg}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Error consultando CTG: {str(e)}",
                "nro_ctg": request.nro_ctg,
                "suggestion": "Token podría haber expirado, obtener nuevo token"
            }
        )