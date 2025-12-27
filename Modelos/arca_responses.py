# Modelos de respuesta ARCA/AFIP
# Estructuras de datos para integración con webservices gubernamentales

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ArcaTokenResponse(BaseModel):
    """
    Respuesta del servicio ARCA para tokens de acceso.
    Usado para CPE, EMBARQUES y FACTURACIÓN.
    """
    success: bool
    token: Optional[str] = None
    sign: Optional[str] = None
    service: str
    service_type: str  # CPE, EMBARQUES, FACTURACION
    environment: str  # PROD, TEST
    timestamp: str
    error: Optional[str] = None
    details: Optional[str] = None


class CartaPorteValidationRequest(BaseModel):
    """
    Request para validar carta de porte contra ARCA.
    """
    numero_carta: str
    cuit_solicitante: str
    token_arca: str
    
    class Config:
        schema_extra = {
            "example": {
                "numero_carta": "12345678901",
                "cuit_solicitante": "20123456789",
                "token_arca": "TOKEN_DE_ACCESO_ARCA"
            }
        }


class CartaPorteValidationResponse(BaseModel):
    """
    Respuesta de validación de carta de porte desde ARCA.
    """
    numero_carta: str
    valida: bool
    estado_carta: str
    coe_numero: Optional[str] = None
    
    # Datos del origen y destino
    origen: Dict[str, Any]
    destino: Dict[str, Any]
    
    # Datos de la mercadería
    cereal: str
    peso_declarado: float
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime] = None
    
    # Datos del transporte
    patente: str
    chofer_datos: Dict[str, str]
    empresa_transporte: str
    
    # Metadatos de validación
    validacion_timestamp: datetime
    mensaje_arca: Optional[str] = None
    errores: Optional[List[str]] = None


class EmbarqueNotificationRequest(BaseModel):
    """
    Request para notificar embarque a ARCA.
    Servicio de Comunicaciones de Embarques.
    """
    numero_carta: str
    buque_nombre: str
    fecha_embarque: datetime
    peso_embarcado: float
    puerto_destino: str
    observaciones: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "numero_carta": "12345678901",
                "buque_nombre": "MV GRAIN CARRIER",
                "fecha_embarque": "2025-12-26T14:30:00Z",
                "peso_embarcado": 25000.0,
                "puerto_destino": "Shanghai",
                "observaciones": "Embarque completo sin observaciones"
            }
        }


class FacturacionRequest(BaseModel):
    """
    Request para facturación electrónica AFIP.
    """
    numero_carta: str
    cuit_cliente: str
    importe_total: float
    servicios_facturados: List[Dict[str, Any]]
    condicion_pago: str = "Contado"
    
    class Config:
        schema_extra = {
            "example": {
                "numero_carta": "12345678901",
                "cuit_cliente": "20123456789",
                "importe_total": 15000.50,
                "servicios_facturados": [
                    {"concepto": "Descarga cereal", "cantidad": 25000, "precio_unitario": 0.50},
                    {"concepto": "Almacenaje", "cantidad": 1, "precio_unitario": 2500.50}
                ],
                "condicion_pago": "30 días"
            }
        }


class SystemStatusResponse(BaseModel):
    """
    Estado general del sistema LogiGrain.
    """
    sistema: str = "LogiGrain - Terminal Portuaria"
    version: str = "1.0.0"
    timestamp: datetime
    
    # Estados por sector
    sectores_status: Dict[str, Dict[str, Any]]
    
    # Estado ARCA
    arca_services: Dict[str, bool]  # CPE, EMBARQUES, FACTURACION
    last_token_refresh: Dict[str, Optional[datetime]]
    
    # Estadísticas operativas
    camiones_en_puerto: int
    cola_espera: int
    promedio_tiempo_procesamiento: int  # minutos
    
    # Alertas
    alertas_activas: List[str] = []
    mantenimiento_programado: Optional[datetime] = None