from Arca.wsaa import create_tra
from Arca.wsaa import sign_tra_cms
from Arca.wsaa import call_wsaa
import base64
from OpenSSL import crypto

# --- Configuración Específica de PRODUCCIÓN ---
CERT_PATH = 'certificado.pem'      # RUTA a tu archivo de certificado (PEM)
KEY_PATH = 'MiClavePrivada.key'    # RUTA a tu archivo de clave privada (PEM)
SERVICE = 'wsfe'                  # Ejemplo: 'wsfe', 'ws_sr_constancia_inscripcion', etc.
WSDL_URL = "https://wsaa.afip.gov.ar/ws/services/LoginCms"
# Usamos la constante de Producción
# --- Fin Configuración ---

print(f"Iniciando solicitud de Token y Sign (TA) al ambiente de PRODUCCIÓN...")

# 1. Crear el TRA
tra_xml = create_tra(SERVICE)

# 2. Firmar el TRA para obtener el CMS en Base64
try:
    cms_base64 = sign_tra_cms(tra_xml, CERT_PATH, KEY_PATH)
except Exception as e:
    print(f"❌ Error crítico en la firma del CMS. Verifica el formato PEM y las rutas de tus archivos.")
    print(f"Detalle: {e}")
    exit()

# 3. Invocar al WSAA
ta_data = call_wsaa(cms_base64, WSDL_URL)

if 'error' in ta_data:
    print(f"\n❌ Error al obtener el TA en Producción:")
    print(f"Detalle del WSAA: {ta_data['error']}")
    print("-" * 40)
    # Algunos errores comunes en producción:
    if "Certificado no emitido por AC de confianza" in ta_data['error'] or "Computador no autorizado" in ta_data['error']:
        print("POSIBLE CAUSA: Estás usando un certificado de Homologación contra el servidor de Producción, o viceversa.") [cite: 745, 750, 751]
    if "Firma inválida" in ta_data['error']:
        print("POSIBLE CAUSA: El mensaje firmado fue mal generado o el certificado/clave son inválidos/expirados.") [cite: 781, 782]
    if "DN del source inválido" in ta_data['error']:
        print("SOLUCIÓN: El WSAA sugiere no incluir los campos 'source' y 'destination' en el TRA (lo cual ya hacemos en el código).") [cite: 763, 764]
else:
    print("\n✅ **Ticket de Acceso (TA) para PRODUCCIÓN Obtenido con Éxito**")
    print("-" * 45)
    print(f"Servicio: {SERVICE}")
    print(f"Token (TA): {ta_data['token'][:20]}...")
    print(f"Sign (TS): {ta_data['sign'][:20]}...")
    print("-" * 45)