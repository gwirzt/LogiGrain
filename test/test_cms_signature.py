"""
Script para probar la nueva implementación de firma CMS
"""

from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=== PRUEBA DE FIRMA CMS CON CRYPTOGRAPHY ===")
print()

try:
    from main import get_arca_config
    from Arca.wsaa import create_tra, sign_tra_cms
    
    # Obtener configuración
    config = get_arca_config()
    print(f"✅ Configuración cargada: {config['service_name']}")
    
    # Crear TRA de prueba
    tra_xml = create_tra(config['service_name'])
    print(f"✅ TRA XML generado: {len(tra_xml)} caracteres")
    
    # Probar firma CMS
    print("🔐 Probando firma CMS con cryptography...")
    cms_base64 = sign_tra_cms(tra_xml, config['cert_file'], config['key_file'])
    
    print(f"✅ CMS generado exitosamente")
    print(f"   Longitud CMS Base64: {len(cms_base64)} caracteres")
    print(f"   Primeros 50 caracteres: {cms_base64[:50]}...")
    
    print()
    print("🎯 CONCLUSIÓN: La nueva implementación funciona correctamente")
    
except Exception as e:
    print(f"❌ Error en la prueba: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)