
import datetime
import random
import xml.etree.ElementTree as ET
import base64

# Dependencias Criptográficas
from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization

# Dependencias SOAP
from zeep import Client, Settings
from lxml import etree 

# Logging centralizado
import sys
import os
# Agregar directorio padre al path para importar utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import setup_logger
logger = setup_logger('arca') 

# --- CONFIGURACIÓN ---
# Puedes cambiar esta constante. Se recomienda GMT-3 (Argentina).
TIMEZONE_OFFSET = -3 
# --- FIN CONFIGURACIÓN ---

def load_keys_and_cert(cert_file, key_file):
    """Carga el certificado y la clave privada de archivos PEM."""
    
    logger.info(f"Cargando certificados SSL: {cert_file}, {key_file}")
    
    try:
        # 1. Cargar la clave privada
        # Se usa 'cryptography' para cargar la clave, ya que es la forma moderna.
        with open(key_file, "rb") as f:
            # Aquí puedes especificar la contraseña si la clave está cifrada (passphrase=b'tu_clave')
            private_key_pem = f.read()
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None # Reemplaza None si tu clave tiene passphrase
            )
        
        # 2. Convertir la clave privada al formato de pyOpenSSL
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key_pem)

        # 3. Cargar el certificado
        with open(cert_file, "rb") as f:
            cert_pem = f.read()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
        
        logger.info("Certificados SSL cargados exitosamente")
        return cert, pkey
        
    except FileNotFoundError as e:
        logger.error(f"Error cargando certificados: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado cargando certificados: {e}")
        raise

def create_tra(service_id):
    """Crea el XML del Ticket Request de Acceso (TRA)."""
    
    logger.info(f"Creando TRA para servicio: {service_id}")
    
    tz = datetime.timezone(datetime.timedelta(hours=TIMEZONE_OFFSET))
    now = datetime.datetime.now(tz)
    
    # Restamos y sumamos 10 minutos para el rango de validez (según manual)
    generation_time = now - datetime.timedelta(minutes=10)
    expiration_time = now + datetime.timedelta(minutes=10)

    unique_id = int(random.random() * 10000000)

    # El formato DEBE ser ISO 8601 con zona horaria (ej: 2025-12-10T15:50:00-03:00)
    fmt = "%Y-%m-%dT%H:%M:%S"
    offset_str = f"{TIMEZONE_OFFSET:+03d}:00"

    tra = ET.Element('loginTicketRequest', attrib={'version': '1.0'})
    
    header = ET.SubElement(tra, 'header')
    ET.SubElement(header, 'uniqueId').text = str(unique_id)
    # Formateamos con el offset de la zona horaria
    ET.SubElement(header, 'generationTime').text = generation_time.strftime(fmt) + offset_str
    ET.SubElement(header, 'expirationTime').text = expiration_time.strftime(fmt) + offset_str
    
    ET.SubElement(tra, 'service').text = service_id

    tra_xml = ET.tostring(tra, encoding='utf-8').decode('utf-8')
    logger.debug(f"TRA XML generado: {tra_xml}")
    
    # Devolvemos el XML como string
    return tra_xml
    expiration_time = now + datetime.timedelta(minutes=10)

    unique_id = int(random.random() * 10000000)

    # El formato DEBE ser ISO 8601 con zona horaria (ej: 2025-12-10T15:50:00-03:00)
    fmt = "%Y-%m-%dT%H:%M:%S"
    offset_str = f"{TIMEZONE_OFFSET:+03d}:00"

    tra = ET.Element('loginTicketRequest', attrib={'version': '1.0'})
    
    header = ET.SubElement(tra, 'header')
    ET.SubElement(header, 'uniqueId').text = str(unique_id)
    # Formateamos con el offset de la zona horaria
    ET.SubElement(header, 'generationTime').text = generation_time.strftime(fmt) + offset_str
    ET.SubElement(header, 'expirationTime').text = expiration_time.strftime(fmt) + offset_str
    
    ET.SubElement(tra, 'service').text = service_id

    # Devolvemos el XML como string
    return ET.tostring(tra, encoding='utf-8').decode('utf-8')


def sign_tra_cms(tra_xml, cert_file, key_file):
    """
    Firma el XML del TRA usando OpenSSL CLI (igual que en VFP).
    Este método replica exactamente la lógica del código VFP funcionando.
    """
    
    logger.info("Firmando TRA con OpenSSL CLI (método VFP)")
    
    import subprocess
    import tempfile
    import os
    from pathlib import Path
    
    try:
        # Obtener directorio base y ruta de OpenSSL
        base_dir = Path(__file__).parent.parent  # LogiGrain root
        openssl_path = base_dir / "Ssl" / "openssl.exe"
        
        logger.info(f"Usando OpenSSL: {openssl_path}")
        
        if not openssl_path.exists():
            raise FileNotFoundError(f"OpenSSL no encontrado: {openssl_path}")
        
        # Crear archivos temporales en el directorio del proyecto
        temp_dir = base_dir / "Ssl" / "TEMP"
        temp_dir.mkdir(exist_ok=True)
        
        tra_file = temp_dir / "requestTA.xml"
        cms_file = temp_dir / "MiLoginTicketRequest.xml.cms"
        
        # 1. Escribir TRA XML a archivo
        logger.info(f"Escribiendo TRA a: {tra_file}")
        with open(tra_file, 'w', encoding='utf-8') as f:
            f.write(tra_xml)
        
        # 2. Construir comando OpenSSL (igual que VFP)
        cmd = [
            str(openssl_path),
            "cms",
            "-sign",
            "-in", str(tra_file),
            "-out", str(cms_file), 
            "-signer", str(cert_file),
            "-inkey", str(key_file),
            "-nodetach",
            "-outform", "PEM"
        ]
        
        logger.info(f"Ejecutando: {' '.join(cmd)}")
        
        # 3. Ejecutar OpenSSL
        result = subprocess.run(
            cmd,
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            logger.error(f"Error OpenSSL: {result.stderr}")
            raise Exception(f"OpenSSL falló: {result.stderr}")
        
        logger.info("OpenSSL ejecutado exitosamente")
        
        # 4. Leer archivo CMS y limpiarlo (igual que VFP)
        if not cms_file.exists():
            raise Exception("Archivo CMS no fue generado")
        
        with open(cms_file, 'r') as f:
            cms_content = f.read()
        
        logger.info(f"CMS generado, longitud original: {len(cms_content)}")
        
        # 5. Limpiar headers/footers (igual que VFP)
        # .archivoCifrado =  LEFT(.archivoCifrado, LEN(.archivoCifrado) - 19) && Quito el final
        # .archivoCifrado = RIGHT(.archivoCifrado, LEN(.archivoCifrado) - 20) && Quito el inicio
        
        # Buscar y remover headers PEM
        lines = cms_content.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Omitir headers y footers de PEM
            if not line.startswith('-----') and line.strip():
                cleaned_lines.append(line.strip())
        
        # Unir todas las líneas en un solo string Base64
        cms_base64 = ''.join(cleaned_lines)
        
        logger.info(f"CMS limpiado, longitud final: {len(cms_base64)}")
        
        # 6. Limpiar archivos temporales (opcional)
        try:
            tra_file.unlink()
            cms_file.unlink()
        except:
            pass  # No es crítico si falla la limpieza
        
        return cms_base64
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout ejecutando OpenSSL")
        raise Exception("Timeout en OpenSSL - proceso demoró más de 30 segundos")
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        raise Exception(f"Error de archivos: {e}")
    except Exception as e:
        logger.error(f"Error firmando TRA con OpenSSL: {e}")
        raise


def call_wsaa(cms_base64, wsdl_url):
    """Invoca el método LoginCms del WSAA para obtener el TA."""

    logger.info(f"Llamando WSAA: {wsdl_url}")
    
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl_url, settings=settings)

    # 1. Invocar el método LoginCms con el CMS Base64
    try:
        logger.debug("Enviando CMS a WSAA...")
        response = client.service.loginCms(in0=cms_base64)
        logger.info("Respuesta WSAA recibida exitosamente")
    except Exception as e:
        # Manejo de errores de la llamada SOAP (ej. error de conexión)
        logger.error(f"Error en la llamada SOAP a WSAA: {e}")
        return {'error': f"Error en la llamada SOAP: {e}"}

    # 2. Procesar la respuesta XML para extraer Token y Sign
    try:
        root = etree.fromstring(response.encode('utf-8'))
    except etree.XMLSyntaxError as e:
        logger.error(f"Respuesta WSAA no es XML válida: {e}")
        return {'error': f"Respuesta no es XML válida: {response}"}

    # Buscar el elemento <credentials>
    credentials = root.find('.//credentials')
    
    if credentials is not None:
        token = credentials.find('token').text
        sign = credentials.find('sign').text
        logger.info("Token y Sign extraídos exitosamente de respuesta WSAA")
        return {
            'token': token,
            'sign': sign
        }
    else:
        # Si no hay credenciales, buscamos si hay un error reportado
        fault_string = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body/{http://schemas.xmlsoap.org/soap/envelope/}Fault/faultstring')
        error_msg = fault_string.text if fault_string is not None else "Respuesta del WSAA no contiene credenciales ni error específico."
        logger.error(f"Error en respuesta WSAA: {error_msg}")
        
        return {'error': error_msg}


class ArcaSettings:
    """Configuración para la integración con ARCA/AFIP WSAA."""
    
    def __init__(self, 
                 service_name: str = "wscpe", 
                 cert_file: str = "Ssl/Nacion1846_1b31e8cd3180840d.crt",
                 key_file: str = "Ssl/MiClavePrivada.key",
                 wsaa_url: str = "https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL"):
        self.service_name = service_name
        self.cert_file = cert_file
        self.key_file = key_file
        self.wsaa_url = wsaa_url
    
    def validate_certificates(self):
        """Valida que los certificados existan."""
        import os
        if not os.path.exists(self.cert_file):
            raise FileNotFoundError(f"Certificado no encontrado: {self.cert_file}")
        if not os.path.exists(self.key_file):
            raise FileNotFoundError(f"Clave privada no encontrada: {self.key_file}")
        return True


def get_arca_access_ticket(service_type="", environment="", custom_config=None):
    """
    Función principal para obtener el Access Ticket de ARCA.
    
    Args:
        service_type: Tipo de servicio ("CPE", "EMBARQUES", "FACTURACION"). Si vacío, usa CPE por defecto
        environment: Entorno ("PROD", "HOMO"). Si vacío, lee del .env
        custom_config: Configuración personalizada. Si None, lee del .env
    
    Ejecuta el flujo completo:
    1. Lee configuración desde .env o parámetros
    2. Valida certificados
    3. Genera XML TRA
    4. Firma el TRA con CMS
    5. Envía petición al WSAA
    6. Retorna token y sign
    """
    
    logger.info(f"Iniciando autenticación ARCA - Tipo: '{service_type}', Entorno: '{environment}'")
    
    try:
        # Obtener configuración
        if custom_config:
            settings = custom_config
        else:
            settings = _get_service_config(service_type, environment)
        
        logger.info(f"Configuración obtenida: servicio={settings.service_name}, cert={settings.cert_file}")
        
        # 1. Validar que existan los certificados
        settings.validate_certificates()
        logger.info("Validación de certificados completada")
        
        # 2. Crear el XML TRA
        tra_xml = create_tra(settings.service_name)
        logger.info("TRA XML generado exitosamente")
        
        # 3. Firmar el TRA con CMS
        logger.info("Firmando TRA con certificados SSL...")
        cms_base64 = sign_tra_cms(tra_xml, settings.cert_file, settings.key_file)
        logger.info("TRA firmado exitosamente con CMS")
        
        # 4. Enviar al WSAA y obtener respuesta
        wsaa_response = call_wsaa(cms_base64, settings.wsaa_url)
        
        # 5. Validar respuesta y retornar resultado
        if 'error' in wsaa_response:
            logger.error(f"Error en WSAA: {wsaa_response['error']}")
            return {
                'success': False,
                'error': wsaa_response['error'],
                'details': 'Error en la comunicación con WSAA'
            }
        
        logger.info("Autenticación ARCA completada exitosamente")
        return {
            'success': True,
            'token': wsaa_response['token'],
            'sign': wsaa_response['sign'],
            'service': settings.service_name,
            'service_type': service_type or 'CPE',
            'environment': environment or 'PROD',
            'timestamp': datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=TIMEZONE_OFFSET))
            ).isoformat()
        }
        
    except FileNotFoundError as e:
        logger.error(f"Certificados no encontrados: {e}")
        return {
            'success': False,
            'error': str(e),
            'details': 'Certificados SSL no encontrados'
        }
    except Exception as e:
        logger.error(f"Error inesperado en autenticación ARCA: {e}")
        return {
            'success': False,
            'error': str(e),
            'details': 'Error inesperado en la autenticación ARCA'
        }


def _get_service_config(service_type="", environment=""):
    """
    Función privada para obtener configuración desde variables de entorno.
    
    Args:
        service_type: "CPE", "EMBARQUES", "FACTURACION"
        environment: "PROD", "HOMO"
    """
    import os
    from pathlib import Path
    
    # Valores por defecto si los parámetros están vacíos
    if not service_type:
        service_type = "CPE"
    if not environment:
        environment = os.getenv('ARCA_ENVIRONMENT', 'PROD')
    
    # Obtener configuración base
    base_dir = Path(__file__).parent.parent  # LogiGrain root
    cert_base_dir = os.getenv('ARCA_CERT_BASE_DIR', 'Ssl\\cert')
    cert_dir = base_dir / cert_base_dir.replace('\\', '/')
    
    # Obtener configuración específica del servicio
    service_configs = {
        "CPE": {
            "service_name": os.getenv('ARCA_CPE_SERVICE_NAME', 'wscpe'),
            "cert_name": os.getenv('ARCA_CPE_CERT_NAME', 'CODE_26e5bc7f203c9970.crt'),
            "key_name": os.getenv('ARCA_CPE_KEY_NAME', 'code.key')
        },
        "EMBARQUES": {
            "service_name": os.getenv('ARCA_EMBARQUES_SERVICE_NAME', 'wconscomunicacionembarque'),
            "cert_name": os.getenv('ARCA_EMBARQUES_CERT_NAME', 'CODE_26e5bc7f203c9970.crt'),
            "key_name": os.getenv('ARCA_EMBARQUES_KEY_NAME', 'code.key')
        },
        "FACTURACION": {
            "service_name": os.getenv('ARCA_FACTURACION_SERVICE_NAME', 'wsfe'),
            "cert_name": os.getenv('ARCA_FACTURACION_CERT_NAME', 'CODE_26e5bc7f203c9970.crt'),
            "key_name": os.getenv('ARCA_FACTURACION_KEY_NAME', 'code.key')
        }
    }
    
    if service_type not in service_configs:
        raise ValueError(f"Tipo de servicio no válido: {service_type}. Opciones: CPE, EMBARQUES, FACTURACION")
    
    config = service_configs[service_type]
    
    # URL según entorno
    if environment == "HOMO":
        wsaa_url = os.getenv('ARCA_WSAA_URL_HOMO', 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL')
    else:
        wsaa_url = os.getenv('ARCA_WSAA_URL_PROD', 'https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL')
    
    # Construir rutas de archivos
    cert_file = str(cert_dir / config["cert_name"])
    key_file = str(cert_dir / config["key_name"])
    
    return ArcaSettings(
        service_name=config["service_name"],
        cert_file=cert_file,
        key_file=key_file,
        wsaa_url=wsaa_url
    )