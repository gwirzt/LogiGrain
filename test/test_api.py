"""
Script para probar los endpoints de la API LogiGrain
"""

import requests
import json
import time

def test_endpoint(url, endpoint_name):
    """Prueba un endpoint de la API"""
    print(f"\n=== Probando {endpoint_name} ===")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa")
            try:
                data = response.json()
                print("Response JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print("Response Text:")
                print(response.text)
        else:
            print("❌ Error en respuesta")
            print("Response:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - El servidor no está ejecutándose")
    except requests.exceptions.Timeout:
        print("❌ Timeout - El servidor no responde")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_arca_endpoint(url, endpoint_name):
    """Prueba un endpoint de ARCA específico"""
    print(f"\n=== Probando {endpoint_name} ===")
    print("⚠️  Este endpoint puede tardar más tiempo por la conexión con AFIP...")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token ARCA obtenido exitosamente")
            data = response.json()
            # No mostrar token completo por seguridad, solo metadata
            if "data" in data:
                token_preview = data["data"]["token"][:20] + "..." if len(data["data"]["token"]) > 20 else data["data"]["token"]
                print(f"Token (preview): {token_preview}")
                print(f"Service: {data['data']['service']}")
                print(f"Timestamp: {data['data']['timestamp']}")
        else:
            print("❌ Error obteniendo token ARCA")
            try:
                error_data = response.json()
                print("Error details:", json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print("Response:", response.text)
                
    except Exception as e:
        print(f"❌ Error en {endpoint_name}: {e}")

if __name__ == "__main__":
    base_url = "http://127.0.0.1:8081"  # Puerto actualizado
    
    # Esperar un poco para que el servidor inicie
    print("Esperando que el servidor inicie...")
    time.sleep(3)
    
    # Probar endpoints básicos
    test_endpoint(f"{base_url}/", "Endpoint Raíz")
    test_endpoint(f"{base_url}/health", "Health Check")
    test_endpoint(f"{base_url}/diagnose-certs", "Diagnóstico de Certificados")
    
    # Probar endpoints ARCA específicos
    test_arca_endpoint(f"{base_url}/get-ticket-cpe", "Token CPE")
    test_arca_endpoint(f"{base_url}/get-ticket-embarques", "Token EMBARQUES")
    test_arca_endpoint(f"{base_url}/get-ticket-facturacion", "Token FACTURACIÓN")
    
    print("\n=== Pruebas completadas ===")