# Modelos Pydantic para requests de consulta CPE
from pydantic import BaseModel, Field
from typing import Optional, List


class ConsultaCPERequest(BaseModel):
    """
    Modelo para request de consulta de Carta de Porte Electrónica.
    Basado en el formato XML correcto de WSCPE.
    """
    token: str = Field(..., description="Token de autenticación ARCA (base64)")
    sign: str = Field(..., description="Firma digital ARCA")
    cuit_representada: str = Field(..., min_length=11, max_length=11, description="CUIT de la empresa representada")
    nro_ctg: str = Field(..., description="Número de CTG (Código de Transporte de Granos)")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+...",
                "sign": "h7PGTYHiX74kLJP1hVx75wh3Qr6TcKlb9Q7zmzufaMya1JiYAZay2xi1fnYF3RhV...",
                "cuit_representada": "30606754538",
                "nro_ctg": "10226304603"
            }
        }


class ConsultaLoteCPERequest(BaseModel):
    """
    Modelo para consulta de múltiples CTGs en lote.
    """
    token: str = Field(..., description="Token de autenticación ARCA (base64)")
    sign: str = Field(..., description="Firma digital ARCA")
    cuit_representada: str = Field(..., min_length=11, max_length=11, description="CUIT de la empresa representada")
    numeros_ctg: List[str] = Field(..., description="Lista de números CTG a consultar")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+...",
                "sign": "h7PGTYHiX74kLJP1hVx75wh3Qr6TcKlb9Q7zmzufaMya1JiYAZay2xi1fnYF3RhV...",
                "cuit_representada": "30606754538",
                "numeros_ctg": ["10226304603", "10226304604", "10226304605"]
            }
        }


class XMLTemplateRequest(BaseModel):
    """
    Modelo para generar template XML de ejemplo.
    """
    cuit_representada: str = Field(..., min_length=11, max_length=11, description="CUIT de la empresa representada")
    nro_ctg: str = Field(..., description="Número de CTG para el template")
    
    class Config:
        schema_extra = {
            "example": {
                "cuit_representada": "30606754538",
                "nro_ctg": "10226304603"
            }
        }