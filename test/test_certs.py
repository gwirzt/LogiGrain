"""
Script de prueba simple para verificar los certificados SSL.
"""

import os
from pathlib import Path

# Obtener ruta base del proyecto
BASE_DIR = Path(__file__).parent.absolute()

# Configuración
CERT_FILE = str(BASE_DIR / "Ssl" / "Nacion1846_1b31e8cd3180840d.crt")
KEY_FILE = str(BASE_DIR / "Ssl" / "MiClavePrivada.key")

print("=== Diagnóstico de Certificados SSL ===")
print(f"Base Directory: {BASE_DIR}")
print(f"Certificado: {CERT_FILE}")
print(f"Clave Privada: {KEY_FILE}")
print()

# Verificar existencia
print("=== Verificación de Archivos ===")
print(f"Certificado existe: {os.path.exists(CERT_FILE)}")
print(f"Clave privada existe: {os.path.exists(KEY_FILE)}")

if os.path.exists(CERT_FILE):
    print(f"Tamaño certificado: {os.path.getsize(CERT_FILE)} bytes")

if os.path.exists(KEY_FILE):
    print(f"Tamaño clave privada: {os.path.getsize(KEY_FILE)} bytes")

print()

# Probar carga de certificados
print("=== Prueba de Carga de Certificados ===")
try:
    from Arca.wsaa import load_keys_and_cert
    cert, pkey = load_keys_and_cert(CERT_FILE, KEY_FILE)
    print("✅ Certificados cargados exitosamente")
    print(f"Tipo certificado: {type(cert)}")
    print(f"Tipo clave privada: {type(pkey)}")
except Exception as e:
    print(f"❌ Error cargando certificados: {e}")

print()

# Probar configuración ARCA
print("=== Prueba de Configuración ARCA ===")
try:
    from Arca.wsaa import ArcaSettings
    settings = ArcaSettings(
        service_name="wscpe",
        cert_file=CERT_FILE,
        key_file=KEY_FILE,
        wsaa_url="https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL"
    )
    settings.validate_certificates()
    print("✅ Configuración ARCA válida")
except Exception as e:
    print(f"❌ Error en configuración ARCA: {e}")