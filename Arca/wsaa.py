
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

# --- CONFIGURACIÓN ---
# Puedes cambiar esta constante. Se recomienda GMT-3 (Argentina).
TIMEZONE_OFFSET = -3 
# --- FIN CONFIGURACIÓN ---

def load_keys_and_cert(cert_file, key_file):
    """Carga el certificado y la clave privada de archivos PEM."""
    
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
        
    return cert, pkey

def create_tra(service_id):
    """Crea el XML del Ticket Request de Acceso (TRA)."""
    
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

    # Devolvemos el XML como string
    return ET.tostring(tra, encoding='utf-8').decode('utf-8')


def sign_tra_cms(tra_xml, cert_file, key_file):
    """
    Firma el XML del TRA usando pyOpenSSL para crear el CMS (PKCS#7).
    """
    
    cert, pkey = load_keys_and_cert(cert_file, key_file)

    # Crear el objeto PKCS#7 (CMS)
    pkcs7 = crypto.PKCS7(
        crypto.FILETYPE_ASN1, 
        crypto.load_pkcs7_data(crypto.FILETYPE_PEM, b'') # Inicialización
    )
    
    # Adjuntar certificado y firmar. Usamos NID_pkcs7_signed_and_data para 'Signed Data'
    pkcs7.add_signer(cert, pkey, "sha256") 
    
    # El contenido a firmar es el TRA XML
    pkcs7.set_content(tra_xml.encode('utf-8'))
    
    # Firmar el contenido. Flags=0 para formato DER (binario)
    pkcs7.sign(flags=0) 
    
    # Exportar el resultado. WSAA espera el CMS en Base64.
    cms_der = crypto.dump_pkcs7(crypto.FILETYPE_ASN1, pkcs7)
    
    # Codificar el DER binario a Base64 para el método LoginCms
    cms_base64 = base64.b64encode(cms_der).decode('utf-8')
    
    return cms_base64


def call_wsaa(cms_base64, wsdl_url):
    """Invoca el método LoginCms del WSAA para obtener el TA."""

    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl_url, settings=settings)

    # 1. Invocar el método LoginCms con el CMS Base64
    try:
        response = client.service.loginCms(in0=cms_base64)
    except Exception as e:
        # Manejo de errores de la llamada SOAP (ej. error de conexión)
        return {'error': f"Error en la llamada SOAP: {e}"}

    # 2. Procesar la respuesta XML para extraer Token y Sign
    try:
        root = etree.fromstring(response.encode('utf-8'))
    except etree.XMLSyntaxError:
        return {'error': f"Respuesta no es XML válida: {response}"}

    # Buscar el elemento <credentials>
    credentials = root.find('.//credentials')
    
    if credentials is not None:
        token = credentials.find('token').text
        sign = credentials.find('sign').text
        return {
            'token': token,
            'sign': sign
        }
    else:
        # Si no hay credenciales, buscamos si hay un error reportado
        fault_string = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body/{http://schemas.xmlsoap.org/soap/envelope/}Fault/faultstring')
        error_msg = fault_string.text if fault_string is not None else "Respuesta del WSAA no contiene credenciales ni error específico."
        
        return {'error': error_msg}