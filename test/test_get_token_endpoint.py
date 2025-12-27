"""
Script para probar el endpoint /get-ticket con la corrección aplicada
"""

import requests
import json
import time

print("=== PRUEBA DEL ENDPOINT /get-ticket ===")
print()

# Esperar que el servidor esté listo
print("⏳ Esperando que el servidor esté disponible...")
time.sleep(2)

try:
    # Probar endpoint básico primero
    print("1️⃣ Probando endpoint /health...")
    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ API disponible")
    else:
        print(f"   ❌ API no disponible: {response.status_code}")
        exit(1)
    
    print()
    print("2️⃣ Probando endpoint /get-ticket...")
    print("   ⚠️  Esto puede tardar 10-30 segundos (conexión con AFIP)...")
    
    # Probar obtención del token ARCA
    start_time = time.time()
    response = requests.get("http://127.0.0.1:8000/get-ticket", timeout=60)
    end_time = time.time()
    
    print(f"   ⏱️  Tiempo de respuesta: {end_time - start_time:.2f} segundos")
    print(f"   📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ TOKEN OBTENIDO EXITOSAMENTE!")
        
        data = response.json()
        if "data" in data:
            token_data = data["data"]
            print(f"   🔑 Token (preview): {token_data['token'][:30]}...")
            print(f"   ✏️  Sign (preview): {token_data['sign'][:30]}...")
            print(f"   🎯 Servicio: {token_data['service']}")
            print(f"   ⏰ Timestamp: {token_data['timestamp']}")
            print(f"   📅 Válido por: {token_data['valid_for']}")
        
        print()
        print("🎉 ¡INTEGRACIÓN ARCA/AFIP COMPLETADA EXITOSAMENTE!")
        
    else:
        print("   ❌ Error obteniendo token")
        print(f"   Response: {response.text}")
        
        try:
            error_data = response.json()
            if "detail" in error_data:
                detail = error_data["detail"]
                print(f"   Error: {detail.get('error', 'N/A')}")
                print(f"   Detalles: {detail.get('details', 'N/A')}")
                print(f"   Sugerencia: {detail.get('suggestion', 'N/A')}")
        except:
            pass

except requests.exceptions.ConnectError:
    print("❌ No se puede conectar al servidor. ¿Está ejecutándose la API?")
except requests.exceptions.Timeout:
    print("❌ Timeout - El servidor tardó demasiado en responder")
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print()
print("=" * 60)