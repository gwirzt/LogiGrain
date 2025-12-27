# Modelos de datos para Cartas de Porte Electrónicas (CPE)
# Integración con servicios ARCA/AFIP para validación documental

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EstadoCamion(str, Enum):
    """Estados posibles de un camión en el sistema."""
    EN_VIAJE = "En Viaje"
    EN_PLAYA = "En Playa" 
    INGRESADO = "Ingresado"
    EN_CALADA = "En Calada"
    POST_CALADA = "Post Calada"
    EN_BALANZA_BRUTO = "En Balanza Bruto"
    DESCARGANDO = "Descargando"
    EN_BALANZA_TARA = "En Balanza Tara"
    SALIDO = "Salido"


class TipoCereal(str, Enum):
    """Tipos de cereales manejados en el puerto."""
    TRIGO = "Trigo"
    MAIZ = "Maíz" 
    SOJA = "Soja"
    GIRASOL = "Girasol"
    CEBADA = "Cebada"
    SORGO = "Sorgo"


class CalidadCereal(str, Enum):
    """Clasificación de calidad post-calada."""
    PREMIUM = "Premium"
    ESTANDAR = "Estándar"
    COMERCIAL = "Comercial"
    RECHAZO = "Rechazo"


class CartaPorteElectronica(SQLModel, table=True):
    """
    Modelo principal para Cartas de Porte Electrónicas.
    Integra con ARCA/AFIP para validación documental.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Datos ARCA/AFIP
    numero_carta: str = Field(index=True, unique=True)
    coe_numero: Optional[str] = Field(default=None)  # Código de Operación Electrónica
    cuit_origen: str = Field(min_length=11, max_length=11)
    cuit_destino: str = Field(min_length=11, max_length=11)
    
    # Datos del cereal
    tipo_cereal: TipoCereal
    peso_declarado: float = Field(gt=0)  # kg
    calidad_origen: Optional[str] = Field(default=None)
    calidad_asignada: Optional[CalidadCereal] = Field(default=None)
    
    # Datos del camión
    patente: str = Field(index=True)
    chofer_cuit: str = Field(min_length=11, max_length=11) 
    empresa_transporte: str
    
    # Control de estado
    estado_actual: EstadoCamion = Field(default=EstadoCamion.EN_VIAJE)
    fecha_ingreso: Optional[datetime] = Field(default=None)
    fecha_salida: Optional[datetime] = Field(default=None)
    
    # Validación ARCA
    validado_arca: bool = Field(default=False)
    fecha_validacion_arca: Optional[datetime] = Field(default=None)
    token_arca_usado: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relaciones
    pesajes: List["Pesaje"] = Relationship(back_populates="carta_porte")
    movimientos: List["MovimientoSector"] = Relationship(back_populates="carta_porte")


class Pesaje(SQLModel, table=True):
    """
    Registro de pesajes en báscula bruto y tara.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relación con carta de porte
    carta_porte_id: int = Field(foreign_key="cartaporteelectronica.id")
    carta_porte: CartaPorteElectronica = Relationship(back_populates="pesajes")
    
    # Datos del pesaje
    tipo_pesaje: str = Field(description="'bruto' o 'tara'")
    peso: float = Field(gt=0)  # kg
    timestamp_pesaje: datetime = Field(default_factory=datetime.utcnow)
    balanza_id: str = Field(description="Identificador de la báscula")
    operador: str
    
    # Datos calculados (solo para tara)
    peso_neto: Optional[float] = Field(default=None)
    diferencia_declarada: Optional[float] = Field(default=None)
    
    # Validación
    ticket_emitido: bool = Field(default=False)
    numero_ticket: Optional[str] = Field(default=None)


class MovimientoSector(SQLModel, table=True):
    """
    Trazabilidad de movimientos por sectores del puerto.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relación con carta de porte
    carta_porte_id: int = Field(foreign_key="cartaporteelectronica.id")
    carta_porte: CartaPorteElectronica = Relationship(back_populates="movimientos")
    
    # Datos del movimiento
    sector_origen: Optional[int] = Field(default=None)
    sector_destino: int
    timestamp_movimiento: datetime = Field(default_factory=datetime.utcnow)
    
    # Estado del sector
    estado_anterior: EstadoCamion
    estado_nuevo: EstadoCamion
    observaciones: Optional[str] = Field(default=None)
    
    # Datos específicos por sector
    puesto_asignado: Optional[str] = Field(default=None)  # Para calada, plataformas
    inspector_asignado: Optional[str] = Field(default=None)  # Para calada
    tiempo_estimado: Optional[int] = Field(default=None)  # minutos
    
    # Validación del movimiento
    autorizado_por: str
    motivo_movimiento: str = Field(default="Flujo operativo normal")