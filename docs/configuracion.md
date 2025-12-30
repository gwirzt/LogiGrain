# Configuración del Sistema - LogiGrain

## ⚙️ Descripción General

Esta guía cubre toda la configuración necesaria para el sistema LogiGrain, incluyendo variables de entorno, certificados SSL, configuración de base de datos y preparación del entorno de desarrollo y producción.

## 📁 Estructura de Configuración

```
LogiGrain/
├── .env                          # Variables de entorno principales
├── .env.example                  # Template para configuración
├── .gitignore                   # Archivos excluidos de git
├── requirements.txt             # Dependencias Python
├── Ssl/                         # Certificados y claves SSL
│   ├── cert/                    # Certificados de producción
│   │   ├── cpe_cert.crt        # Cert ARCA CPE
│   │   ├── cpe_private.key     # Clave privada CPE
│   │   ├── embarques_cert.crt  # Cert ARCA EMBARQUES
│   │   └── facturacion_cert.crt # Cert ARCA FACTURACION
│   └── TEMP/                   # Certificados de testing
│       ├── test_cert.crt
│       └── test_private.key
└── logigrain.db                # Base de datos SQLite
```

## 🔐 Variables de Entorno

### Archivo `.env` Principal

```bash
# ===================================
# CONFIGURACIÓN GENERAL DEL SISTEMA
# ===================================

# Entorno de ejecución
ENVIRONMENT=DEV                    # DEV, TEST, PROD

# Configuración Base de Datos
DATABASE_URL=sqlite:///./logigrain.db
DATABASE_ECHO=False               # True para ver queries SQL

# JWT Authentication
JWT_SECRET_KEY=supersecretkey123456789abcdef
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=8   # 8 horas de duración

# ===================================
# ARCA/AFIP CONFIGURACIÓN POR SERVICIO
# ===================================

# Servicio CPE (Cartas de Porte Electrónica)
ARCA_CPE_SERVICE_NAME=wscpe
ARCA_CPE_CERT_FILE=Ssl/cert/cpe_cert.crt
ARCA_CPE_KEY_FILE=Ssl/cert/cpe_private.key
ARCA_CPE_WSAA_URL=https://wsaa.afip.gov.ar/ws/services/LoginCms
ARCA_CPE_BASE_URL=https://serviciosweb.afip.gob.ar

# Servicio EMBARQUES (Comunicaciones)
ARCA_EMBARQUES_SERVICE_NAME=wsembarques
ARCA_EMBARQUES_CERT_FILE=Ssl/cert/embarques_cert.crt
ARCA_EMBARQUES_KEY_FILE=Ssl/cert/embarques_private.key
ARCA_EMBARQUES_WSAA_URL=https://wsaa.afip.gov.ar/ws/services/LoginCms
ARCA_EMBARQUES_BASE_URL=https://serviciosweb.afip.gob.ar

# Servicio FACTURACIÓN (Electrónica)
ARCA_FACTURACION_SERVICE_NAME=wsfacturacion
ARCA_FACTURACION_CERT_FILE=Ssl/cert/facturacion_cert.crt
ARCA_FACTURACION_KEY_FILE=Ssl/cert/facturacion_private.key
ARCA_FACTURACION_WSAA_URL=https://wsaa.afip.gov.ar/ws/services/LoginCms
ARCA_FACTURACION_BASE_URL=https://serviciosweb.afip.gob.ar

# ===================================
# CONFIGURACIÓN ESPECÍFICA DE ENTORNO
# ===================================

# URLs por Entorno (PROD/TEST)
WSAA_URL_PROD=https://wsaa.afip.gov.ar/ws/services/LoginCms
WSAA_URL_TEST=https://wsaahomo.afip.gov.ar/ws/services/LoginCms

# Timezone (Argentina GMT-3)
TIMEZONE_OFFSET=-3

# ===================================
# CONFIGURACIÓN OPENSSL
# ===================================

# Comando OpenSSL (ajustar según OS)
OPENSSL_CMD=openssl               # Linux/Mac
# OPENSSL_CMD=C:\OpenSSL\bin\openssl.exe  # Windows con OpenSSL instalado

# Configuración CMS
CMS_DETACHED_SIGNATURE=true
CMS_BINARY_FORMAT=false

# ===================================
# CONFIGURACIÓN DE LOGGING
# ===================================

LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
LOG_MAX_SIZE=5242880             # 5MB en bytes
LOG_BACKUP_COUNT=10              # Cantidad de archivos rotados
LOG_TO_CONSOLE=true              # Solo en DEV

# ===================================
# CONFIGURACIÓN TERMINAL PORTUARIA
# ===================================

# Información de la empresa
EMPRESA_CUIT=20123456789
EMPRESA_NOMBRE=LogiGrain Terminales SA
EMPRESA_EMAIL=admin@logigrain.com

# Puertos disponibles
DEFAULT_PUERTO=TRP1

# ===================================
# CONFIGURACIÓN CACHE
# ===================================

# Cache de tokens ARCA
ARCA_TOKEN_CACHE_HOURS=8         # Duración cache (sincronizado con JWT)
CACHE_CLEANUP_INTERVAL=3600      # Limpieza cada hora (en segundos)

# ===================================
# CONFIGURACIÓN API
# ===================================

API_HOST=127.0.0.1
API_PORT=8080
API_RELOAD=true                  # Hot reload en DEV
API_DEBUG=true                   # Información debug en DEV

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_METHODS=["GET", "POST", "PUT", "DELETE"]
CORS_HEADERS=["Authorization", "Content-Type"]
```

### Template `.env.example`

```bash
# ===================================
# TEMPLATE DE CONFIGURACIÓN - LOGIGRAIN
# ===================================
# Copie este archivo como .env y configure los valores apropiados

# CONFIGURACIÓN GENERAL
ENVIRONMENT=DEV
DATABASE_URL=sqlite:///./logigrain.db
JWT_SECRET_KEY=YOUR_SECRET_KEY_HERE_CHANGE_IN_PRODUCTION
JWT_ACCESS_TOKEN_EXPIRE_HOURS=8

# CERTIFICADOS ARCA - CONFIGURAR RUTAS REALES
ARCA_CPE_CERT_FILE=Ssl/TEMP/test_cert.crt
ARCA_CPE_KEY_FILE=Ssl/TEMP/test_private.key
# ... (resto de configuración igual)

# OPENSSL - CONFIGURAR SEGÚN SO
OPENSSL_CMD=openssl  # Linux/Mac
# OPENSSL_CMD=C:\OpenSSL\bin\openssl.exe  # Windows

# DATOS EMPRESA - CONFIGURAR CON DATOS REALES
EMPRESA_CUIT=YOUR_COMPANY_CUIT
EMPRESA_NOMBRE=Your Company Name
```

## 🛡️ Gestión de Certificados SSL

### Estructura de Certificados

```
Ssl/
├── cert/                        # Producción (NO commitear)
│   ├── cpe_cert.crt            # Certificado CPE firmado por AFIP
│   ├── cpe_private.key         # Clave privada CPE
│   ├── embarques_cert.crt      # Certificado EMBARQUES
│   ├── embarques_private.key   # Clave privada EMBARQUES
│   ├── facturacion_cert.crt    # Certificado FACTURACION
│   └── facturacion_private.key # Clave privada FACTURACION
└── TEMP/                       # Testing (commiteables)
    ├── test_cert.crt           # Certificado autofirmado para testing
    └── test_private.key        # Clave privada de testing
```

### Generación de Certificados de Testing

```bash
# Navegar al directorio SSL/TEMP
cd Ssl/TEMP

# Generar clave privada
openssl genpkey -algorithm RSA -out test_private.key -pkcs8 -aes256

# Generar certificado autofirmado (válido por 365 días)
openssl req -new -x509 -key test_private.key -out test_cert.crt -days 365 \
    -subj "/C=AR/ST=Buenos Aires/L=Buenos Aires/O=LogiGrain Test/CN=test.logigrain.com"

# Verificar certificado generado
openssl x509 -in test_cert.crt -text -noout
```

### Configuración de Certificados AFIP Reales

```bash
# 1. Obtener certificado desde AFIP
# - Ingresar a https://auth.afip.gob.ar/contribuyente_/
# - Generar solicitud de certificado para servicios web
# - Descargar certificado firmado

# 2. Copiar certificados a directorio producción
cp certificado_afip.crt Ssl/cert/cpe_cert.crt
cp clave_privada.key Ssl/cert/cpe_private.key

# 3. Verificar certificado AFIP
openssl x509 -in Ssl/cert/cpe_cert.crt -text -noout
```

### Validación de Certificados

```python
# Script de validación automática
import ssl
import socket
from datetime import datetime
import os

def validate_certificate(cert_path: str, key_path: str) -> dict:
    """Validar certificado SSL y su clave correspondiente"""
    
    validation_result = {
        "cert_path": cert_path,
        "key_path": key_path,
        "valid": False,
        "errors": [],
        "info": {}
    }
    
    try:
        # Verificar existencia de archivos
        if not os.path.exists(cert_path):
            validation_result["errors"].append(f"Certificado no encontrado: {cert_path}")
            return validation_result
            
        if not os.path.exists(key_path):
            validation_result["errors"].append(f"Clave privada no encontrada: {key_path}")
            return validation_result
        
        # Cargar y validar certificado
        with open(cert_path, 'rb') as cert_file:
            cert = ssl.load_certificate(ssl.FILETYPE_PEM, cert_file.read())
            
            # Información del certificado
            validation_result["info"] = {
                "subject": dict(cert.get_subject().get_components()),
                "issuer": dict(cert.get_issuer().get_components()),
                "serial": cert.get_serial_number(),
                "version": cert.get_version(),
                "not_before": cert.get_notBefore().decode(),
                "not_after": cert.get_notAfter().decode(),
            }
            
            # Verificar expiración
            not_after = datetime.strptime(
                cert.get_notAfter().decode(), 
                '%Y%m%d%H%M%SZ'
            )
            
            if not_after < datetime.utcnow():
                validation_result["errors"].append("Certificado expirado")
            elif (not_after - datetime.utcnow()).days < 30:
                validation_result["errors"].append(
                    f"Certificado expira pronto: {not_after.strftime('%Y-%m-%d')}"
                )
        
        # Verificar que clave corresponde al certificado
        # (Implementación específica según necesidades)
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
    except Exception as e:
        validation_result["errors"].append(f"Error de validación: {str(e)}")
    
    return validation_result

# Uso
for service in ["cpe", "embarques", "facturacion"]:
    cert_path = f"Ssl/cert/{service}_cert.crt"
    key_path = f"Ssl/cert/{service}_private.key"
    result = validate_certificate(cert_path, key_path)
    print(f"Certificado {service}: {'✅ Válido' if result['valid'] else '❌ Error'}")
    if result['errors']:
        for error in result['errors']:
            print(f"  - {error}")
```

## 🗄️ Configuración de Base de Datos

### SQLite (Desarrollo/Testing)

```python
# Configuración en main.py
from sqlmodel import SQLModel, create_engine, Session

# URL de conexión desde .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./logigrain.db")
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,  # Log queries SQL si está habilitado
    connect_args={"check_same_thread": False}  # Solo para SQLite
)

def create_database_and_tables():
    """Crear todas las tablas de la base de datos"""
    SQLModel.metadata.create_all(engine)
    
def get_session():
    """Obtener sesión de base de datos"""
    with Session(engine) as session:
        yield session
```

### Migración a PostgreSQL (Producción)

```bash
# Instalar dependencias adicionales
pip install psycopg2-binary alembic

# Variables .env para PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/logigrain
DATABASE_ECHO=False

# Configuración de conexión
POSTGRES_USER=logigrain_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=logigrain_prod
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

```python
# engine para PostgreSQL
from sqlmodel import create_engine

DATABASE_URL = (f"postgresql://{os.getenv('POSTGRES_USER')}:"
               f"{os.getenv('POSTGRES_PASSWORD')}@"
               f"{os.getenv('POSTGRES_HOST')}:"
               f"{os.getenv('POSTGRES_PORT')}/"
               f"{os.getenv('POSTGRES_DB')}")

engine = create_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,
    pool_size=10,          # Pool de conexiones
    max_overflow=20,       # Conexiones adicionales
    pool_timeout=30,       # Timeout para obtener conexión
    pool_recycle=1800      # Reciclar conexiones cada 30min
)
```

## 🚀 Configuración de Entornos

### Desarrollo (DEV)

```bash
# .env para desarrollo
ENVIRONMENT=DEV
DATABASE_URL=sqlite:///./logigrain.db
DATABASE_ECHO=true

# Certificados de testing
ARCA_CPE_CERT_FILE=Ssl/TEMP/test_cert.crt
ARCA_CPE_KEY_FILE=Ssl/TEMP/test_private.key

# URLs de testing AFIP
WSAA_URL=https://wsaahomo.afip.gov.ar/ws/services/LoginCms

# Logging detallado
LOG_LEVEL=DEBUG
LOG_TO_CONSOLE=true

# API con hot reload
API_RELOAD=true
API_DEBUG=true
```

### Testing (TEST)

```bash
# .env.test
ENVIRONMENT=TEST
DATABASE_URL=sqlite:///./test_logigrain.db

# Certificados de testing
ARCA_CPE_CERT_FILE=Ssl/TEMP/test_cert.crt

# URLs de homologación AFIP
WSAA_URL=https://wsaahomo.afip.gov.ar/ws/services/LoginCms

# Logging reducido para tests
LOG_LEVEL=WARNING
LOG_TO_CONSOLE=false

# Sin hot reload para tests
API_RELOAD=false
API_DEBUG=false
```

### Producción (PROD)

```bash
# .env.prod
ENVIRONMENT=PROD
DATABASE_URL=postgresql://user:password@db:5432/logigrain

# Certificados reales AFIP
ARCA_CPE_CERT_FILE=Ssl/cert/cpe_cert.crt
ARCA_CPE_KEY_FILE=Ssl/cert/cpe_private.key

# URLs de producción AFIP
WSAA_URL=https://wsaa.afip.gov.ar/ws/services/LoginCms

# JWT secret fuerte
JWT_SECRET_KEY=ultra_secure_production_key_256_bits_minimum

# Logging optimizado
LOG_LEVEL=INFO
LOG_TO_CONSOLE=false

# API optimizada
API_RELOAD=false
API_DEBUG=false
```

## 📦 Gestión de Dependencias

### `requirements.txt` Principal

```txt
# ===================================
# DEPENDENCIAS CORE DEL SISTEMA
# ===================================

# FastAPI y servidor
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Base de datos y ORM
sqlmodel==0.0.14
sqlalchemy==2.0.23

# Autenticación JWT
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Integración ARCA/AFIP
pyopenssl==23.3.0
cryptography==41.0.7
zeep==4.2.1
lxml==4.9.3
requests==2.31.0

# Configuración y entorno
python-dotenv==1.0.0
pydantic-settings==2.1.0

# Logging y utilidades
python-json-logger==2.0.7

# ===================================
# DEPENDENCIAS DE DESARROLLO
# ===================================

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Linting y formateo
flake8==6.1.0
black==23.11.0
isort==5.12.0

# Documentación
mkdocs==1.5.3
mkdocs-material==9.4.8

# ===================================
# DEPENDENCIAS OPCIONALES
# ===================================

# PostgreSQL (solo en producción)
# psycopg2-binary==2.9.9
# alembic==1.12.1

# Monitoreo avanzado
# prometheus-client==0.19.0
# sentry-sdk[fastapi]==1.38.0

# Excel/CSV processing
# pandas==2.1.3
# openpyxl==3.1.2
```

### Instalación por Entorno

```bash
# Desarrollo - instalar todo
pip install -r requirements.txt

# Producción - solo dependencias core
pip install fastapi uvicorn sqlmodel python-jose passlib pyopenssl \
           cryptography zeep lxml requests python-dotenv pydantic-settings

# Testing - agregar dependencias de test
pip install pytest pytest-asyncio httpx
```

## 🔧 Scripts de Configuración

### Script de Inicialización `setup.py`

```python
#!/usr/bin/env python3
"""
Script de inicialización del sistema LogiGrain
Configura entorno, valida certificados, inicializa base de datos
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def setup_environment():
    """Configurar entorno inicial"""
    print("🔧 Configurando entorno LogiGrain...")
    
    # Crear .env si no existe
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("✅ Archivo .env creado desde template")
        else:
            print("❌ No se encontró .env.example para crear .env")
            return False
    
    # Crear directorios necesarios
    directories = [
        "logs",
        "Ssl/cert",
        "Ssl/TEMP",
        "test/temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio creado/verificado: {directory}")
    
    return True

def validate_dependencies():
    """Validar dependencias del sistema"""
    print("\n📋 Validando dependencias...")
    
    # Verificar OpenSSL
    try:
        result = subprocess.run(["openssl", "version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ OpenSSL: {result.stdout.strip()}")
        else:
            print("❌ OpenSSL no disponible")
            return False
    except FileNotFoundError:
        print("❌ OpenSSL no está instalado")
        return False
    
    # Verificar Python packages
    required_packages = [
        "fastapi", "sqlmodel", "cryptography", 
        "zeep", "python-jose", "passlib"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Instalar dependencias faltantes:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def generate_test_certificates():
    """Generar certificados de testing si no existen"""
    print("\n🔐 Generando certificados de testing...")
    
    cert_path = Path("Ssl/TEMP/test_cert.crt")
    key_path = Path("Ssl/TEMP/test_private.key")
    
    if cert_path.exists() and key_path.exists():
        print("✅ Certificados de testing ya existen")
        return True
    
    try:
        # Generar clave privada
        subprocess.run([
            "openssl", "genpkey", "-algorithm", "RSA", 
            "-out", str(key_path), "-pkcs8"
        ], check=True)
        
        # Generar certificado autofirmado
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", str(key_path),
            "-out", str(cert_path), "-days", "365",
            "-subj", "/C=AR/ST=Buenos Aires/L=Buenos Aires/O=LogiGrain Test/CN=test"
        ], check=True)
        
        print("✅ Certificados de testing generados")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generando certificados: {e}")
        return False

def initialize_database():
    """Inicializar base de datos"""
    print("\n🗄️ Inicializando base de datos...")
    
    try:
        # Importar y ejecutar init_db
        sys.path.append(".")
        import init_db
        
        print("✅ Base de datos inicializada")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando BD: {e}")
        return False

def main():
    """Función principal de setup"""
    print("🚀 Iniciando configuración de LogiGrain\n")
    
    steps = [
        ("Configurar entorno", setup_environment),
        ("Validar dependencias", validate_dependencies),
        ("Generar certificados testing", generate_test_certificates),
        ("Inicializar base de datos", initialize_database)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Falló: {step_name}")
            sys.exit(1)
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Revisar y ajustar .env según tus necesidades")
    print("2. Configurar certificados AFIP reales (si es producción)")
    print("3. Ejecutar: python main.py")
    print("4. Abrir: http://127.0.0.1:8080/docs")

if __name__ == "__main__":
    main()
```

### Script de Validación `validate.py`

```python
#!/usr/bin/env python3
"""
Script de validación integral del sistema LogiGrain
"""

import os
import sys
from pathlib import Path
import sqlite3
from dotenv import load_dotenv

def validate_env_file():
    """Validar archivo .env"""
    print("🔍 Validando archivo .env...")
    
    if not Path(".env").exists():
        print("❌ Archivo .env no encontrado")
        return False
    
    load_dotenv()
    
    required_vars = [
        "JWT_SECRET_KEY",
        "ARCA_CPE_SERVICE_NAME",
        "ARCA_CPE_CERT_FILE",
        "ARCA_CPE_KEY_FILE"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {', '.join(missing_vars)}")
        return False
    
    print("✅ Archivo .env válido")
    return True

def validate_certificates():
    """Validar certificados SSL"""
    print("🔐 Validando certificados...")
    
    load_dotenv()
    cert_file = os.getenv("ARCA_CPE_CERT_FILE")
    key_file = os.getenv("ARCA_CPE_KEY_FILE")
    
    if not cert_file or not Path(cert_file).exists():
        print(f"❌ Certificado no encontrado: {cert_file}")
        return False
    
    if not key_file or not Path(key_file).exists():
        print(f"❌ Clave privada no encontrada: {key_file}")
        return False
    
    print("✅ Certificados disponibles")
    return True

def validate_database():
    """Validar base de datos"""
    print("🗄️ Validando base de datos...")
    
    db_path = "logigrain.db"
    if not Path(db_path).exists():
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas esenciales
        tables = ["usuario", "puerto", "usuariopuerto", "arcatoken"]
        for table in tables:
            cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone()[0] == 0:
                print(f"❌ Tabla faltante: {table}")
                return False
        
        conn.close()
        print("✅ Base de datos válida")
        return True
        
    except Exception as e:
        print(f"❌ Error validando BD: {e}")
        return False

def main():
    """Validación completa"""
    print("🧪 Iniciando validación del sistema\n")
    
    validations = [
        ("Archivo .env", validate_env_file),
        ("Certificados SSL", validate_certificates),
        ("Base de datos", validate_database)
    ]
    
    all_valid = True
    for name, validation_func in validations:
        if not validation_func():
            all_valid = False
        print()
    
    if all_valid:
        print("🎉 ¡Sistema validado exitosamente!")
        print("✅ Listo para ejecutar: python main.py")
    else:
        print("❌ Sistema tiene errores de configuración")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 🐳 Configuración Docker

### `Dockerfile`

```dockerfile
# Multi-stage build para optimizar tamaño
FROM python:3.11-slim as base

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    openssl \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no root
RUN useradd --create-home --shell /bin/bash logigrain

# Configurar directorio de trabajo
WORKDIR /app
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Etapa de producción
FROM base as production

# Copiar código
COPY --chown=logigrain:logigrain . .

# Crear directorios necesarios
RUN mkdir -p logs Ssl/cert && \
    chown -R logigrain:logigrain logs Ssl

# Cambiar a usuario no root
USER logigrain

# Exponer puerto
EXPOSE 8080

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  logigrain:
    build: .
    ports:
      - "8080:8080"
    env_file:
      - .env.prod
    volumes:
      - ./Ssl:/app/Ssl:ro
      - ./logs:/app/logs
      - logigrain_data:/app/data
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: logigrain
      POSTGRES_USER: logigrain_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - logigrain

volumes:
  postgres_data:
  logigrain_data:
```

## 📊 Monitoreo y Métricas

### Configuración Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'logigrain'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
```

### Configuración Grafana

```json
{
  "dashboard": {
    "title": "LogiGrain System Metrics",
    "panels": [
      {
        "title": "Requests per Second",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

## 🧪 Testing de Configuración

### Test Suite

```python
import pytest
import os
from pathlib import Path

class TestConfiguration:
    """Test suite para validar configuración"""
    
    def test_env_file_exists(self):
        """Test que .env existe"""
        assert Path(".env").exists(), "Archivo .env no encontrado"
    
    def test_required_env_vars(self):
        """Test variables de entorno requeridas"""
        from dotenv import load_dotenv
        load_dotenv()
        
        required = [
            "JWT_SECRET_KEY",
            "ARCA_CPE_SERVICE_NAME",
            "DATABASE_URL"
        ]
        
        for var in required:
            assert os.getenv(var), f"Variable requerida no encontrada: {var}"
    
    def test_certificates_exist(self):
        """Test que certificados existen"""
        from dotenv import load_dotenv
        load_dotenv()
        
        cert_file = os.getenv("ARCA_CPE_CERT_FILE")
        key_file = os.getenv("ARCA_CPE_KEY_FILE")
        
        assert cert_file and Path(cert_file).exists(), f"Certificado no encontrado: {cert_file}"
        assert key_file and Path(key_file).exists(), f"Clave no encontrada: {key_file}"
    
    def test_database_connection(self):
        """Test conexión a base de datos"""
        from sqlmodel import create_engine, Session
        from dotenv import load_dotenv
        
        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        engine = create_engine(DATABASE_URL)
        with Session(engine) as session:
            # Test simple query
            result = session.exec("SELECT 1").first()
            assert result == 1
```

## 📚 Referencias

- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/) - Configuración avanzada FastAPI
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Gestión de configuración
- [Python Dotenv](https://pypi.org/project/python-dotenv/) - Manejo de variables de entorno
- [OpenSSL Commands](https://www.openssl.org/docs/man1.1.1/man1/) - Comandos OpenSSL
- [SQLModel](https://sqlmodel.tiangolo.com/) - ORM y base de datos
- [Docker Compose](https://docs.docker.com/compose/) - Orquestación de contenedores