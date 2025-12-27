# Rutas FastAPI para Balanzas (Bruto y Tara)
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/balanzas", tags=["Balanzas"])

@router.get("/")
async def get_balanzas_status() -> Dict[str, Any]:
    """
    Estado actual del sistema de balanzas.
    Incluye báscula bruto (sector 7) y báscula tara (sector 9).
    """
    return {
        "sector": "Balanzas",
        "sectores_incluidos": [7, 9],
        "descripcion": "Registro pesos, cálculo neto, emisión tickets",
        "balanzas": {
            "bascula_bruto": {
                "sector_id": 7,
                "status": "operational",
                "capacidad_maxima": "80000 kg",
                "precision": "±10 kg"
            },
            "bascula_tara": {
                "sector_id": 9, 
                "status": "operational",
                "capacidad_maxima": "80000 kg",
                "precision": "±10 kg"
            }
        }
    }

@router.post("/pesar-bruto")
async def pesar_bruto(patente: str, numero_carta: str) -> Dict[str, Any]:
    """
    Registra el peso bruto del camión cargado.
    Asigna plataforma de descarga según tipo de cereal.
    """
    logger.info(f"Pesaje bruto - Patente: {patente}, Carta: {numero_carta}")
    
    # TODO: Integrar con hardware de báscula real
    peso_bruto_simulado = 52500  # kg
    
    return {
        "patente": patente,
        "numero_carta": numero_carta,
        "peso_bruto": peso_bruto_simulado,
        "timestamp": "2025-12-26T17:45:00",
        "plataforma_asignada": "P-3",
        "status": "peso_bruto_registrado",
        "proximo_sector": "plataforma_descarga"
    }

@router.post("/pesar-tara")
async def pesar_tara(patente: str, numero_carta: str) -> Dict[str, Any]:
    """
    Registra el peso tara del camión vacío.
    Calcula peso neto y emite ticket final.
    """
    logger.info(f"Pesaje tara - Patente: {patente}, Carta: {numero_carta}")
    
    # TODO: Integrar con hardware de báscula real
    peso_tara_simulado = 27500  # kg
    peso_bruto_simulado = 52500  # kg - obtener de BD
    peso_neto = peso_bruto_simulado - peso_tara_simulado
    
    return {
        "patente": patente,
        "numero_carta": numero_carta,
        "peso_tara": peso_tara_simulado,
        "peso_bruto": peso_bruto_simulado,
        "peso_neto": peso_neto,
        "timestamp": "2025-12-26T18:15:00",
        "ticket_emitido": True,
        "status": "pesaje_completo",
        "proximo_sector": "porteria_egreso"
    }