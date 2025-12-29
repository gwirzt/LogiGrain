# Utils - Utilidades del Sistema

## Propósito del Módulo

El módulo **Utils** contiene utilidades transversales y servicios auxiliares que son utilizados por todos los sectores del sistema LogiGrain. Proporciona funcionalidades comunes como logging, validaciones, formateo de datos y herramientas de debugging.

## Componentes del Módulo

### Archivos de Utilidades
- `logger.py` - Configuración centralizada de logging del sistema
- `__init__.py` - Inicialización del módulo de utilidades

## Logger Centralizado

### Propósito del Logger
- **Logging unificado**: Configuración estándar para todo el sistema
- **Rotación de archivos**: Gestión automática de tamaño y archivos históricos
- **Niveles configurable**: Debug, Info, Warning, Error por módulo
- **Formato consistente**: Timestamps, niveles y contexto estandarizados

### Configuración del Logger
```python
import logging
import logging.handlers
from datetime import datetime
import os

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO):
    """
    Configura logger con formato estándar LogiGrain.
    
    Args:
        name: Nombre del logger (generalmente __name__ del módulo)
        log_file: Archivo de log específico (opcional)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger configurado
    """
```

### Uso en Sectores
```python
# En cualquier módulo del sistema
from utils.logger import setup_logger

logger = setup_logger(__name__, 'playa_camiones.log')

logger.info("Camión ingresado a playa: patente ABC123")
logger.warning("CPE con diferencia de peso: 2.5%")
logger.error("Error comunicación ARCA: timeout")
```

## Utilidades de Validación

### Validadores de Documentos
```python
def validar_cuit(cuit: str) -> bool:
    """Valida formato y dígito verificador de CUIT argentino."""
    
def validar_patente(patente: str) -> bool:
    """Valida formato de patente argentina (AAA123 o AB123CD)."""
    
def validar_numero_cpe(numero_cpe: str) -> bool:
    """Valida formato de número de Carta de Porte Electrónica."""
```

### Validadores de Cereales
```python
def validar_parametros_calidad(cereal: str, parametros: dict) -> dict:
    """
    Valida parámetros de calidad según normas por cereal.
    
    Args:
        cereal: Tipo de cereal ("TRIGO", "MAIZ", "SOJA")
        parametros: Dict con humedad, impurezas, etc.
        
    Returns:
        Dict con validaciones y observaciones
    """
    
def calcular_grado_calidad(cereal: str, analisis: dict) -> str:
    """Calcula grado de calidad según análisis y normas."""
```

## Utilidades de Formateo

### Formateo de Datos
```python
def format_peso(peso_kg: float) -> str:
    """Formatea peso con separadores de miles y 2 decimales."""
    return f"{peso_kg:,.2f} kg"

def format_timestamp_argentina(dt: datetime) -> str:
    """Formatea timestamp en zona horaria argentina."""
    return dt.strftime("%d/%m/%Y %H:%M:%S GMT-3")

def format_cuit(cuit: str) -> str:
    """Formatea CUIT con guiones: 12-34567890-1"""
    return f"{cuit[:2]}-{cuit[2:10]}-{cuit[10]}"

def format_patente(patente: str) -> str:
    """Formatea patente con espacios: ABC 123 o AB 123 CD"""
```

### Generadores de Números
```python
def generar_numero_operacion() -> str:
    """Genera número único de operación: OPyyyymmdd###"""
    
def generar_id_trazabilidad() -> str:
    """Genera ID único para trazabilidad: TR{timestamp}{random}"""
    
def generar_numero_ticket(sector: str) -> str:
    """Genera número de ticket por sector: BB{yyyymmdd}{###}"""
```

## Utilidades de Configuración

### Gestión de Variables de Entorno
```python
def get_config_value(key: str, default: Any = None, required: bool = False) -> Any:
    """
    Obtiene valor de configuración desde .env con validación.
    
    Args:
        key: Clave de configuración
        default: Valor por defecto
        required: Si es obligatorio (lanza excepción si falta)
    """

def validate_env_config() -> dict:
    """
    Valida que todas las variables críticas estén configuradas.
    Returns dict con status de configuración.
    """
```

### Configuración por Sector
```python
def get_sector_config(sector: str) -> dict:
    """
    Obtiene configuración específica de un sector.
    
    Sectors: PLAYA, PORTERIA_INGRESO, CALADA, BALANZAS, PORTERIA_EGRESO
    """

def get_arca_config(service: str = "CPE") -> dict:
    """Obtiene configuración específica de servicio ARCA."""
```

## Utilidades de Fechas y Tiempo

### Manejo de Timezone Argentina
```python
from datetime import datetime, timezone, timedelta

ARGENTINA_TZ = timezone(timedelta(hours=-3))

def now_argentina() -> datetime:
    """Retorna datetime actual en timezone Argentina (GMT-3)."""
    return datetime.now(ARGENTINA_TZ)

def to_argentina_time(dt: datetime) -> datetime:
    """Convierte datetime UTC a timezone Argentina."""
    
def format_for_arca(dt: datetime) -> str:
    """Formatea datetime para servicios ARCA (ISO 8601 GMT-3)."""
```

### Cálculos Operativos
```python
def calcular_tiempo_ciclo(fecha_ingreso: datetime, fecha_egreso: datetime) -> dict:
    """Calcula tiempo total de ciclo y descomposición por sectores."""
    
def calcular_demoras(operacion_id: int) -> dict:
    """Calcula demoras por sector basado en timestamps registrados."""
```

## Utilidades de Archivos

### Gestión de Archivos Temporales
```python
def create_temp_file(content: str, suffix: str = '.tmp') -> str:
    """Crea archivo temporal y retorna path."""
    
def cleanup_temp_files(older_than_hours: int = 24):
    """Limpia archivos temporales antiguos."""
    
def backup_file(file_path: str, backup_dir: str = './backups') -> str:
    """Crea backup de archivo con timestamp."""
```

### Archivos de Log
```python
def rotate_log_files(log_dir: str = './logs', keep_days: int = 30):
    """Rota archivos de log manteniendo histórico configurado."""
    
def compress_old_logs(log_dir: str = './logs'):
    """Comprime logs antiguos para ahorrar espacio."""
```

## Utilidades de Performance

### Decoradores de Medición
```python
import time
from functools import wraps

def measure_time(logger_name: str = None):
    """Decorator que mide tiempo de ejecución de función."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            log = logging.getLogger(logger_name or func.__module__)
            log.info(f"{func.__name__} ejecutado en {duration:.3f}s")
            return result
        return wrapper
    return decorator

def async_measure_time(logger_name: str = None):
    """Decorator async que mide tiempo de ejecución."""
```

### Cache Simple
```python
from typing import Dict, Any
import time

class SimpleCache:
    """Cache en memoria simple con TTL."""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Any:
        """Obtiene valor del cache si no expiró."""
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Guarda valor en cache con TTL."""
        
    def clear_expired(self):
        """Limpia entradas expiradas."""
```

## Utilidades de Testing

### Datos de Prueba
```python
def generar_cuit_test() -> str:
    """Genera CUIT válido para testing."""
    
def generar_patente_test() -> str:
    """Genera patente válida para testing."""
    
def generar_operacion_test() -> dict:
    """Genera datos completos de operación para testing."""
    
def generar_analisis_test(cereal: str) -> dict:
    """Genera análisis de calidad válido para testing."""
```

### Mocks y Stubs
```python
class MockArcaResponse:
    """Mock de respuesta ARCA para testing."""
    
class MockBasculaReading:
    """Mock de lectura de báscula para testing."""
    
def create_test_database():
    """Crea base de datos temporal para tests."""
```

## Utilidades de Seguridad

### Sanitización de Datos
```python
def sanitize_input(text: str) -> str:
    """Sanitiza input del usuario removiendo caracteres peligrosos."""
    
def validate_file_upload(file_content: bytes, allowed_types: list) -> bool:
    """Valida contenido y tipo de archivo subido."""
    
def hash_sensitive_data(data: str) -> str:
    """Hashea datos sensibles para logging seguro."""
```

## Configuración de Logging por Módulo

### Estructura de Logs
```
logs/
├── main.log              # Log principal de la aplicación
├── arca/
│   ├── wsaa.log         # Logs específicos WSAA
│   └── cpe_queries.log  # Logs de consultas CPE
├── sectores/
│   ├── playa.log        # Logs Playa de Camiones
│   ├── calada.log       # Logs Sector Calada
│   ├── balanzas.log     # Logs Sistema Balanzas
│   └── porterias.log    # Logs Porterías
└── archived/
    └── {year}/
        └── {month}/     # Logs archivados por mes
```

### Configuración por Entorno
```python
# Desarrollo
LOG_LEVEL = DEBUG
LOG_TO_CONSOLE = True
LOG_TO_FILE = True

# Producción  
LOG_LEVEL = INFO
LOG_TO_CONSOLE = False
LOG_TO_FILE = True
LOG_ROTATION = True
```

## Comandos de Utilidad

### Limpieza y Mantenimiento
```python
def cleanup_system():
    """Ejecuta tareas de limpieza del sistema."""
    cleanup_temp_files()
    rotate_log_files()
    compress_old_logs()

def health_check() -> dict:
    """Verifica salud del sistema y configuración."""
    return {
        "config_valid": validate_env_config(),
        "disk_space": check_disk_space(),
        "log_files": check_log_files(),
        "temp_files": count_temp_files()
    }
```

## Uso en Desarrollo

### Debugging
```python
from utils.logger import setup_logger
from utils.decorators import measure_time

logger = setup_logger(__name__, level=logging.DEBUG)

@measure_time("performance")
def proceso_pesado():
    logger.debug("Iniciando proceso pesado")
    # ... lógica compleja
    logger.debug("Proceso completado")
```

### Testing
```python
from utils.testing import generar_operacion_test, MockArcaResponse

def test_validacion_cpe():
    operacion = generar_operacion_test()
    mock_response = MockArcaResponse(success=True)
    # ... test logic
```

## Configuración del Módulo

```env
# Variables específicas para Utils
LOG_LEVEL=INFO
LOG_TO_CONSOLE=false
LOG_ROTATION_SIZE=10MB
LOG_RETENTION_DAYS=30
TEMP_CLEANUP_HOURS=24
CACHE_DEFAULT_TTL=300
TIMEZONE_OFFSET=-3
```

## Contacto y Mantenimiento

Para consultas sobre utilidades o problemas de logging:
- **DevOps Team**: devops@logigrain.com
- **Logging Issues**: logs@logigrain.com
- **Performance**: performance@logigrain.com
- **Configuración**: config@logigrain.com

## Extensión del Módulo

Para agregar nuevas utilidades:

1. **Crear función en módulo apropiado**
2. **Agregar tests correspondientes** 
3. **Documentar en este README**
4. **Actualizar configuración .env si necesario**
5. **Notificar a equipos afectados**

Las utilidades deben ser:
- ✅ **Reutilizables** por múltiples sectores
- ✅ **Bien documentadas** con docstrings
- ✅ **Testeadas** con casos de prueba
- ✅ **Performantes** para uso frecuente
- ✅ **Seguras** para datos sensibles