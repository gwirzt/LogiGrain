"""
Script para probar la configuración ARCA desde variables de entorno
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Agregar directorio padre al path para importar módulos
BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(BASE_DIR))

# Cargar variables de entorno
load_dotenv()

print("=== Configuración ARCA desde .env ===")
print(f"BASE_DIR: {BASE_DIR}")
print()

# Leer variables de entorno
cert_base_dir = os.getenv('ARCA_CERT_BASE_DIR', 'Ssl\\cert')
cert_name = os.getenv('ARCA_CERT_NAME', 'Nacion1846_1b31e8cd3180840d.crt')
key_name = os.getenv('ARCA_KEY_NAME', '..\\MiClavePrivada.key')

print("=== Variables de entorno ===")
print(f"ARCA_CERT_BASE_DIR: {cert_base_dir}")
print(f"ARCA_CERT_NAME: {cert_name}")
print(f"ARCA_KEY_NAME: {key_name}")
print()

# Construir rutas
cert_dir = BASE_DIR / cert_base_dir.replace('\\', '/')
cert_file = str(cert_dir / cert_name)
key_file = str(cert_dir / key_name.replace('\\', '/'))

print("=== Rutas construidas ===")
print(f"Directorio certificados: {cert_dir}")
print(f"Archivo certificado: {cert_file}")
print(f"Archivo clave privada: {key_file}")
print()

# Verificar existencia
print("=== Verificación de archivos ===")
print(f"Certificado existe: {os.path.exists(cert_file)}")
print(f"Clave privada existe: {os.path.exists(key_file)}")

if os.path.exists(cert_file):
    print(f"Tamaño certificado: {os.path.getsize(cert_file)} bytes")

if os.path.exists(key_file):
    print(f"Tamaño clave privada: {os.path.getsize(key_file)} bytes")

print()

# Probar carga de certificados
print("=== Prueba de carga ARCA ===")
try:
    from Arca.wsaa import ArcaSettings
    settings = ArcaSettings(
        service_name="wscpe",
        cert_file=cert_file,
        key_file=key_file,
        wsaa_url="https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL"
    )
    settings.validate_certificates()
    print("✅ Configuración ARCA válida desde .env")
except Exception as e:
    print(f"❌ Error en configuración ARCA: {e}")
    print("Sugerencia: Verifica las rutas en el archivo .env")

print()
print("=== Configuración desde main.py ===")
try:
    # Simular la función de main.py
    from main import get_arca_config
    config = get_arca_config()
    print("Configuración obtenida:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print("✅ Configuración main.py funcional")
except Exception as e:
    print(f"❌ Error importando configuración: {e}")