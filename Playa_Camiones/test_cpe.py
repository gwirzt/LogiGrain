# Ejemplo de uso directo con tu token y sign obtenidos
# Script para probar consultas CPE con datos reales

from Playa_Camiones.wscpe_client import WSCPEClient
import asyncio


async def test_consulta_cpe():
    """
    Test con tu token y sign reales obtenidos.
    """
    
    # Tu token y sign obtenidos
    token_real = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+CiAgICA8aWQgc3JjPSJDTj13c2FhLCBPPUFGSVAsIEM9QVIsIFNFUklBTE5VTUJFUj1DVUlUIDMzNjkzNDUwMjM5IiB1bmlxdWVfaWQ9IjIwNTQwMjA1NDIiIGdlbl90aW1lPSIxNzY2NzgxMDk2IiBleHBfdGltZT0iMTc2NjgyNDM1NiIvPgogICAgPG9wZXJhdGlvbiB0eXBlPSJsb2dpbiIgdmFsdWU9ImdyYW50ZWQiPgogICAgICAgIDxsb2dpbiBlbnRpdHk9IjMzNjkzNDUwMjM5IiBzZXJ2aWNlPSJ3c2NwZSIgdWlkPSJTRVJJQUxOVU1CRVI9Q1VJVCAyMDE3MjQyMDkzMiwgQ049bmFjaW9uMTg0NiIgYXV0aG1ldGhvZD0iY21zIiByZWdtZXRob2Q9IjIyIj4KICAgICAgICAgICAgPHJlbGF0aW9ucz4KICAgICAgICAgICAgICAgIDxyZWxhdGlvbiBrZXk9IjMwNjA2NzU0NTM4IiByZWx0eXBlPSI0Ii8+CiAgICAgICAgICAgIDwvcmVsYXRpb25zPgogICAgICAgIDwvbG9naW4+CiAgICA8L29wZXJhdGlvbj4KPC9zc28+Cg=="
    sign_real = "D0aHXKEpS/Z9klY8VmQgTtLfVMjEWeSzLKY/WNqoyoMrhbmODHb9UQV0AEOGmV71VUEHvrghuCNR7SZhuuNBxG+ysAczQhgjd76Wy91wk4ey+b0zMfp8RBfdVeQI/5Vh3wtbH25Y1w3isYSXUax4iG3NAAhq+DNzWPVzEZa9V/4="
    
    # Número de CPE de ejemplo para probar
    numero_cpe_test = "12345678901"
    
    # Crear cliente y consultar
    client = WSCPEClient()
    resultado = await client.consultar_carta_porte(token_real, sign_real, numero_cpe_test)
    
    print("=== RESULTADO CONSULTA CPE ===")
    print(f"Success: {resultado['success']}")
    print(f"Timestamp: {resultado['timestamp']}")
    
    if resultado['success']:
        print("=== DATOS CPE ===")
        for key, value in resultado['data'].items():
            print(f"{key}: {value}")
    else:
        print(f"Error: {resultado['error']}")


if __name__ == "__main__":
    # Ejecutar test
    asyncio.run(test_consulta_cpe())