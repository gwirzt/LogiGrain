"""
Configuración de logging para LogiGrain.
Centraliza el manejo de logs para ARCA/AFIP y operaciones del sistema.
"""

import logging
import sys
from datetime import datetime

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Configura un logger para el sistema LogiGrain.
    
    Args:
        name: Nombre del logger (ej: 'arca', 'main', 'operations')
        level: Nivel de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Solo configurar si no tiene handlers (evitar duplicados)
    if not logger.handlers:
        # Nivel de logging
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Formato de mensaje
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para archivo (logs/logigrain.log)
        try:
            import os
            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler("logs/logigrain.log", encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"No se pudo crear archivo de log: {e}")
    
    return logger

# Logger global para ARCA
arca_logger = setup_logger('arca')

# Logger global para API
api_logger = setup_logger('api')