"""
Configuración de logging para LogiGrain.
Centraliza el manejo de logs para ARCA/AFIP y operaciones del sistema.
"""

import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Configura un logger para el sistema LogiGrain con rotación de archivos.
    
    Args:
        name: Nombre del logger (ej: 'arca', 'main', 'operations')
        level: Nivel de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    
    Returns:
        Logger configurado con rotación de archivos
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
        
        # Handler para archivo con rotación
        try:
            os.makedirs("logs", exist_ok=True)
            # Rotación: 5MB por archivo, mantener 10 archivos históricos
            file_handler = RotatingFileHandler(
                "logs/logigrain.log", 
                maxBytes=5*1024*1024,  # 5MB
                backupCount=10,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"No se pudo crear archivo de log con rotación: {e}")
    
    return logger

# Logger global para ARCA
arca_logger = setup_logger('arca')

# Logger global para API
api_logger = setup_logger('api')