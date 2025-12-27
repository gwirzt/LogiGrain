"""
Script para verificar los archivos de certificado y clave configurados en .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=== VERIFICACIÓN DE CERTIFICADOS Y CLAVES ===")
print()

# Obtener configuración desde .env
cert_base_dir = os.getenv('ARCA_CERT_BASE_DIR', 'Ssl\\cert')
cert_name = os.getenv('ARCA_CERT_NAME', 'CODE_26e5bc7f203c9970.crt')
key_name = os.getenv('ARCA_KEY_NAME', 'code.key')

BASE_DIR = Path(__file__).parent.absolute()
cert_dir = BASE_DIR / cert_base_dir.replace('\\', '/')

print("📂 CONFIGURACIÓN DESDE .ENV:")
print(f"   ARCA_CERT_BASE_DIR: {cert_base_dir}")
print(f"   ARCA_CERT_NAME: {cert_name}")
print(f"   ARCA_KEY_NAME: {key_name}")
print()

# Construir rutas completas
cert_file = cert_dir / cert_name
key_file = cert_dir / key_name

print("🔍 RUTAS CONSTRUIDAS:")
print(f"   Directorio base: {cert_dir}")
print(f"   Certificado: {cert_file}")
print(f"   Clave privada: {key_file}")
print()

print("✅ VERIFICACIÓN DE EXISTENCIA:")
cert_exists = cert_file.exists()
key_exists = key_file.exists()

print(f"   Certificado existe: {'✅ SÍ' if cert_exists else '❌ NO'}")
if cert_exists:
    print(f"   Tamaño certificado: {cert_file.stat().st_size} bytes")
    print(f"   Fecha modificación: {cert_file.stat().st_mtime}")

print(f"   Clave privada existe: {'✅ SÍ' if key_exists else '❌ NO'}")
if key_exists:
    print(f"   Tamaño clave privada: {key_file.stat().st_size} bytes")
    print(f"   Fecha modificación: {key_file.stat().st_mtime}")

print()

if cert_exists and key_exists:
    print("🔐 PRUEBA DE CARGA DE CERTIFICADOS:")
    try:
        from Arca.wsaa import load_keys_and_cert
        cert, pkey = load_keys_and_cert(str(cert_file), str(key_file))
        
        print("   ✅ Certificados cargados exitosamente")
        print(f"   Tipo certificado: {type(cert)}")
        print(f"   Tipo clave privada: {type(pkey)}")
        
        # Intentar obtener información del certificado
        try:
            subject = cert.get_subject()
            print(f"   Subject: {subject}")
            print(f"   Issuer: {cert.get_issuer()}")
            print(f"   Serial Number: {cert.get_serial_number()}")
            
            # Verificar si el certificado ha expirado
            if cert.has_expired():
                print("   ⚠️  ADVERTENCIA: El certificado ha EXPIRADO")
            else:
                print("   ✅ Certificado vigente")
                
        except Exception as e:
            print(f"   ⚠️  No se pudo leer información del certificado: {e}")
        
    except Exception as e:
        print(f"   ❌ Error cargando certificados: {e}")
        print("   💡 Sugerencia: Verificar que el certificado y clave sean compatibles")

else:
    print("❌ NO SE PUEDEN CARGAR LOS CERTIFICADOS:")
    if not cert_exists:
        print(f"   • Certificado no encontrado: {cert_file}")
    if not key_exists:
        print(f"   • Clave privada no encontrada: {key_file}")
    
    print()
    print("📋 ARCHIVOS DISPONIBLES EN EL DIRECTORIO:")
    if cert_dir.exists():
        crt_files = list(cert_dir.glob("*.crt"))
        key_files = list(cert_dir.glob("*.key"))
        
        print("   Certificados (.crt):")
        for f in crt_files:
            print(f"     • {f.name}")
        
        print("   Claves privadas (.key):")
        for f in key_files:
            print(f"     • {f.name}")

print()
print("=" * 60)