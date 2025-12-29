# ARCA - Integración Multi-Servicio AFIP

## Propósito del Módulo

El módulo **ARCA** es el corazón de la integración con servicios gubernamentales argentinos (AFIP). Gestiona la autenticación y comunicación con **3 servicios ARCA diferentes**: CPE (Cartas de Porte), EMBARQUES (Comunicaciones) y FACTURACION (Electrónica), proporcionando tokens de acceso y firma digital para todas las operaciones del sistema.

## Servicios ARCA Integrados

### 1. CPE - Cartas de Porte Electrónicas
- **Propósito**: Validación y consulta de cartas de porte de cereales
- **Webservice**: `wscpe` - Consulta y actualización de CPE
- **Uso principal**: [Playa de Camiones](../Playa_Camiones/) y [Portería Egreso](../Porteria_Egreso/)
- **Certificado**: CPE específico para transporte de granos

### 2. EMBARQUES - Comunicaciones de Embarques  
- **Propósito**: Notificación de embarques y movimientos portuarios
- **Webservice**: `wsembarques` - Registro de operaciones de embarque
- **Uso principal**: Comunicación con autoridades portuarias y aduaneras
- **Certificado**: EMBARQUES específico para operaciones portuarias

### 3. FACTURACION - Facturación Electrónica
- **Propósito**: Emisión de facturas electrónicas AFIP
- **Webservice**: `wsfev1` - Facturación electrónica versión 1
- **Uso principal**: Facturación de servicios portuarios y comisiones
- **Certificado**: FACTURACION específico para emisión fiscal

## Componentes Técnicos

### Archivos del Módulo
- `wsaa.py` - Módulo WSAA multi-servicio con autenticación AFIP
- `Pruebas/wsaa.http` - Tests HTTP para validación de endpoints

### Arquitectura WSAA

```python
# Función principal parameterless
def get_arca_access_ticket(service: str = "CPE") -> dict:
    """
    Obtiene token y sign para cualquiera de los 3 servicios ARCA.
    Lee configuración automáticamente desde .env
    """
```

## Configuración Multi-Servicio

### Variables de Entorno por Servicio
```env
# SERVICIO CPE
ARCA_CPE_SERVICE_NAME=wscpe
ARCA_CPE_CERT_FILE=./Ssl/cert/cpe_certificate.crt  
ARCA_CPE_KEY_FILE=./Ssl/cert/cpe_private_key.key
ARCA_CPE_WSAA_URL=https://wsaa.afip.gov.ar/ws/services/LoginCms

# SERVICIO EMBARQUES  
ARCA_EMBARQUES_SERVICE_NAME=wsembarques
ARCA_EMBARQUES_CERT_FILE=./Ssl/cert/embarques_certificate.crt
ARCA_EMBARQUES_KEY_FILE=./Ssl/cert/embarques_private_key.key
ARCA_EMBARQUES_WSAA_URL=https://wsaa.afip.gov.ar/ws/services/LoginCms

# SERVICIO FACTURACION
ARCA_FACTURACION_SERVICE_NAME=wsfev1
ARCA_FACTURACION_CERT_FILE=./Ssl/cert/facturacion_certificate.crt  
ARCA_FACTURACION_KEY_FILE=./Ssl/cert/facturacion_private_key.key
ARCA_FACTURACION_WSAA_URL=https://wsaa.afip.gov.ar/ws/services/LoginCms

# CONFIGURACIÓN GENERAL
ARCA_CUIT_SOLICITANTE=33693450239
TIMEZONE_OFFSET=-3
```

## Protocolo WSAA (Web Services Authentication Authorization)

### Flujo de Autenticación
```
1. Generación TRA (Ticket Request Access)
   - Timestamp GMT-3 Argentina
   - Service específico (CPE/EMBARQUES/FACTURACION)
   - CUIT solicitante
   
2. Firma Digital CMS
   - Certificado SSL específico por servicio
   - OpenSSL CLI signing
   - Formato base64
   
3. Request SOAP a AFIP
   - TRA firmado como parámetro
   - Webservice LoginCms
   
4. Response con Credentials
   - Token base64 (12 horas vigencia)
   - Sign digital
   - Expiration timestamp
```

### Implementación OpenSSL CLI
```python
# Firma CMS usando subprocess (compatible AFIP)
def sign_tra_with_openssl(tra_xml: str, cert_file: str, key_file: str) -> str:
    cmd = [
        'openssl', 'cms', '-sign', '-in', tra_temp_file,
        '-signer', cert_file, '-inkey', key_file,
        '-outform', 'base64', '-nodetach'
    ]
    return subprocess.check_output(cmd).decode('utf-8')
```

## Gestión de Certificados SSL

### Estructura de Certificados
```
Ssl/
├── cert/
│   ├── cpe_certificate.crt          # Certificado CPE
│   ├── cpe_private_key.key          # Clave privada CPE
│   ├── embarques_certificate.crt    # Certificado EMBARQUES
│   ├── embarques_private_key.key    # Clave privada EMBARQUES  
│   ├── facturacion_certificate.crt  # Certificado FACTURACION
│   └── facturacion_private_key.key  # Clave privada FACTURACION
└── TEMP/                            # Archivos temporales signing
```

### Validación Automática
- ✅ Verificación de existencia de archivos
- ✅ Validación de formato X.509
- ✅ Control de fechas de vigencia  
- ✅ Verificación de correspondencia cert-key
- ✅ Test de firma CMS funcional

## Endpoints FastAPI Disponibles

### Obtención de Tokens
```http
GET /get-ticket              # Token CPE (por defecto)
GET /get-ticket-cpe          # Token CPE específico
GET /get-ticket-embarques    # Token EMBARQUES específico  
GET /get-ticket-facturacion  # Token FACTURACION específico
```

### Diagnóstico y Testing
```http
GET /diagnose-certs          # Diagnóstico multi-servicio certificados
GET /docs                    # Documentación Swagger automática
```

### Respuestas Estándar
```json
{
  "status": "success",
  "service": "CPE|EMBARQUES|FACTURACION", 
  "token": "base64_token_12h_validity",
  "sign": "digital_signature",
  "expiration": "2025-12-30T14:30:00-03:00",
  "generated_at": "2025-12-29T02:30:00-03:00"
}
```

## Uso en Sectores Operativos

### Playa de Camiones
```python
# Validación CPE de camión
from Arca.wsaa import get_arca_access_ticket
from Playa_Camiones.wscpe_client import WSCPEClient

# Obtener credenciales CPE
creds = get_arca_access_ticket("CPE")
client = WSCPEClient()

# Consultar carta de porte
result = await client.consultar_carta_porte(
    creds["token"], 
    creds["sign"], 
    cuit_empresa, 
    numero_ctg
)
```

### Facturación Servicios
```python
# Emisión factura electrónica
creds = get_arca_access_ticket("FACTURACION") 
# Usar token/sign para webservice facturación
```

### Comunicación Embarques
```python
# Notificación operaciones portuarias
creds = get_arca_access_ticket("EMBARQUES")
# Usar token/sign para notificar embarques
```

## Manejo de Errores y Logging

### Tipos de Error
- **Certificado no encontrado**: Verificar rutas en .env
- **Certificado vencido**: Renovar con AFIP
- **Error de firma CMS**: Verificar OpenSSL instalado
- **Timeout AFIP**: Reintentar con delay exponencial
- **Token expirado**: Re-autenticar automáticamente

### Logging Detallado
```python
import logging
logger = logging.getLogger(__name__)

# Logs específicos por servicio y operación
logger.info(f"Solicitando token {service} para CUIT {cuit}")
logger.error(f"Error autenticación {service}: {error_details}")
```

## Características Técnicas

### Timezone Argentina
```python
TIMEZONE_OFFSET = -3  # GMT-3 Argentina
# Todos los timestamps en horario local argentino
```

### Formato XML TRA
```xml
<?xml version="1.0" encoding="UTF-8"?>
<loginTicketRequest version="1.0">
    <header>
        <uniqueId>{{timestamp}}</uniqueId>
        <generationTime>{{iso8601_gmt_minus_3}}</generationTime>
        <expirationTime>{{iso8601_plus_24h}}</expirationTime>
    </header>
    <service>{{CPE|EMBARQUES|FACTURACION}}</service>
    <destination>{{CUIT_SOLICITANTE}}</destination>
</loginTicketRequest>
```

## Seguridad y Compliance

### Protocolos de Seguridad
- 🔒 Certificados SSL específicos por servicio
- 🔒 Firma digital CMS compatible AFIP
- 🔒 Tokens con expiración automática (12h)
- 🔒 No persistencia de credenciales sensibles
- 🔒 Logs auditables de todas las operaciones

### Compliance AFIP
- ✅ Protocolo WSAA oficial
- ✅ Timezone Argentina GMT-3
- ✅ Formato XML según especificación
- ✅ Certificados homologados AFIP
- ✅ Trazabilidad completa de operaciones

## Configuración de Desarrollo vs Producción

### Entorno de Testing
```env
# URLs de testing AFIP
ARCA_*_WSAA_URL=https://wsaahomo.afip.gov.ar/ws/services/LoginCms
```

### Entorno de Producción  
```env
# URLs de producción AFIP
ARCA_*_WSAA_URL=https://wsaa.afip.gov.ar/ws/services/LoginCms
```

## Monitoreo y Métricas

### KPIs de Integración
- Tiempo promedio de obtención de token
- Tasa de éxito autenticación por servicio
- Disponibilidad webservices AFIP
- Frecuencia de re-autenticación
- Errores por tipo y servicio

### Alertas Automáticas
- Certificados próximos a vencer (30 días)
- Fallos consecutivos de autenticación
- Timeouts prolongados con AFIP
- Errores de configuración .env

## Contacto y Soporte

Para consultas sobre integración ARCA o problemas de autenticación:
- **Equipo AFIP Integration**: extension-afip@logigrain.com
- **Soporte Certificados**: certs@logigrain.com  
- **Emergencias ARCA**: Protocolo 24hs disponible
- **AFIP Mesa de Ayuda**: 0800-999-2347

## Documentación Oficial AFIP

- [Manual WSAA](https://www.afip.gob.ar/ws/documentacion/wsaa.asp)
- [Webservice CPE](https://www.afip.gob.ar/ws/documentacion/wscpe.asp)
- [Certificados Digitales](https://www.afip.gob.ar/ws/certificados/)
- [Ambientes de Testing](https://www.afip.gob.ar/ws/ambientes/)