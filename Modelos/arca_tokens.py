"""
Modelos para el sistema de cache de tokens ARCA/AFIP
==================================================

Este módulo contiene los modelos SQLModel para el manejo de cache
de tokens y signs de ARCA/AFIP, evitando solicitudes innecesarias.

Características:
- Cache por usuario y puerto específico
- Validación automática de expiración (8 horas)
- Tipos de servicio: CPE, EMBARQUES, FACTURACION
- Timestamps con zona horaria Argentina (GMT-3)
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel


class ArcaToken(SQLModel, table=True):
    """
    Modelo para cache de tokens ARCA/AFIP.
    
    Almacena tokens y signs obtenidos de ARCA para evitar 
    solicitudes repetidas dentro del período de validez.
    """
    __tablename__ = "arca_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    puerto_codigo: str = Field(max_length=10, index=True)
    servicio_tipo: str = Field(max_length=20, index=True)  # CPE, EMBARQUES, FACTURACION
    
    # Datos del token ARCA
    token: str = Field(max_length=2000)  # Token XML de ARCA
    sign: str = Field(max_length=1000)   # Sign de autenticación
    
    # Control de fechas
    fecha_solicitud: datetime = Field(default_factory=datetime.utcnow)
    fecha_vencimiento: datetime  # Se calcula como fecha_solicitud + 8 horas
    
    # Metadatos adicionales
    wsaa_url: Optional[str] = Field(default=None, max_length=200)
    servicio_nombre: Optional[str] = Field(default=None, max_length=50)
    
    # Relaciones
    usuario: "Usuario" = Relationship(back_populates="arca_tokens")
    
    def __init__(self, **data):
        """Inicializar token con cálculo automático de fecha de vencimiento."""
        if "fecha_vencimiento" not in data and "fecha_solicitud" in data:
            data["fecha_vencimiento"] = data["fecha_solicitud"] + timedelta(hours=8)
        elif "fecha_vencimiento" not in data:
            fecha_solicitud = datetime.utcnow()
            data["fecha_solicitud"] = fecha_solicitud
            data["fecha_vencimiento"] = fecha_solicitud + timedelta(hours=8)
        
        super().__init__(**data)
    
    def is_expired(self) -> bool:
        """Verificar si el token ha expirado."""
        return datetime.utcnow() >= self.fecha_vencimiento
    
    def tiempo_restante(self) -> timedelta:
        """Obtener tiempo restante de validez del token."""
        return self.fecha_vencimiento - datetime.utcnow()


# Modelos de request para endpoints con puerto
class ArcaTokenRequest(BaseModel):
    """Request model para solicitudes de token ARCA con puerto específico."""
    puerto_codigo: str = Field(..., min_length=3, max_length=10, description="Código del puerto (ej: TRP1, TSL1)")


class ArcaTokenResponse(BaseModel):
    """Response model unificado para tokens ARCA con información de cache."""
    status: str
    message: str
    data: dict
    cache_info: dict  # Información sobre si se usó cache o se solicitó nuevo token


# Extensión del modelo Usuario para relación con tokens
from .usuario import Usuario

# Agregar la relación al modelo Usuario existente
Usuario.model_rebuild()