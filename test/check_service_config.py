"""
Script para revisar la configuración del servicio ARCA/AFIP WSAA
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=== CONFIGURACIÓN DE CONEXIÓN ARCA/AFIP ===")
print()

# Importar configuración desde main.py
try:
    from main import get_arca_config
    config = get_arca_config()
    
    print("📋 CONFIGURACIÓN ACTUAL:")
    print(f"   Servicio ARCA: {config['service_name']}")
    print(f"   URL WSAA: {config['wsaa_url']}")
    print()
    
    print("🔍 DETALLES DEL SERVICIO:")
    service_name = config['service_name']
    wsaa_url = config['wsaa_url']
    
    # Explicar el servicio
    if service_name == "wscpe":
        print("   ✅ Servicio: CPE (Carta de Porte Electrónica)")
        print("   📝 Descripción: WebService para Cartas de Porte de Granos")
        print("   🎯 Propósito: Validar cartas de porte de cereales y oleaginosas")
    else:
        print(f"   ⚠️  Servicio: {service_name} (verificar si es el correcto)")
    
    # Explicar la URL
    print()
    print("🌐 DETALLES DE CONEXIÓN:")
    if "wsaa.afip.gov.ar" in wsaa_url:
        print("   🏢 Entorno: PRODUCCIÓN AFIP")
        print("   ⚠️  ADVERTENCIA: Conectándose al servidor REAL de AFIP")
        print("   📋 Servicio: LoginCms (WSAA - Web Service de Autenticación y Autorización)")
    elif "wsaahomo.afip.gov.ar" in wsaa_url:
        print("   🧪 Entorno: HOMOLOGACIÓN AFIP")
        print("   ✅ Entorno de pruebas - Seguro para testing")
    else:
        print(f"   ❓ URL desconocida: {wsaa_url}")
    
    print()
    print("🔑 CERTIFICADOS:")
    print(f"   Certificado: {config['cert_file']}")
    print(f"   Clave privada: {config['key_file']}")
    print(f"   Existe certificado: {os.path.exists(config['cert_file'])}")
    print(f"   Existe clave privada: {os.path.exists(config['key_file'])}")
    
    print()
    print("⚡ FLUJO DE AUTENTICACIÓN:")
    print("   1. Genera XML TRA (Ticket Request Access) para servicio 'wscpe'")
    print("   2. Firma el TRA con certificado SSL usando CMS/PKCS#7")
    print("   3. Envía CMS firmado a WSAA de AFIP via SOAP")
    print("   4. AFIP responde con TOKEN y SIGN válidos por 24 horas")
    print("   5. TOKEN + SIGN se usan para acceder al WebService CPE")
    
    print()
    print("🎯 PRÓXIMOS PASOS:")
    print("   • El token obtenido se usará para:")
    print("     - Consultar cartas de porte por QR")
    print("     - Validar documentos de transporte")
    print("     - Verificar datos de exportadores")
    print("     - Integrar con flujo de terminal portuaria")

except ImportError as e:
    print(f"❌ Error importando configuración: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print()
print("=" * 50)

# Información adicional sobre servicios ARCA disponibles
print()
print("📚 OTROS SERVICIOS ARCA DISPONIBLES:")
print("   • wscpe - Carta de Porte Electrónica (ACTUAL)")
print("   • wscdc - Código de Trazabilidad de Granos (CTG)")
print("   • wsctg - WebService CTG") 
print("   • wsconstrans - Consulta de Transportes")
print()
print("💡 NOTA: Para cambiar de servicio, modificar 'service_name' en main.py")