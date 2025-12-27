# Instrucciones para LogiGrain - Sistema de Terminal Portuaria

## Arquitectura del Sistema

**LogiGrain** es un sistema integral de gestión para terminal portuaria que automatiza el flujo completo desde la llegada de camiones hasta su salida. El sistema maneja cereales de exportación e integra con servicios gubernamentales argentinos (ARCA/AFIP) para validación documental.

### Componentes Principales

- **FastAPI Backend** ([main.py](main.py)) - API principal con 7 endpoints ARCA multi-servicio
- **Integración ARCA Multi-Servicio** ([Arca/wsaa.py](Arca/wsaa.py)) - Módulo WSAA con soporte para 3 servicios AFIP: CPE, EMBARQUES, FACTURACION
- **Configuración .env** ([.env](.env)) - Variables de entorno para certificados y URLs por servicio
- **Modelos de Datos** ([Modelos/usuario.py](Modelos/usuario.py)) - Esquemas SQLModel para usuarios, items y relaciones
- **Gestión SSL** ([Ssl/](Ssl/)) - Certificados SSL específicos por servicio ARCA

## Flujo Operativo y Sectores

El sistema modela **10 sectores operativos** conectados siguiendo el flujo físico de camiones:
1. **Playa de Camiones** (20km) → Recepción, validación ARCA, facturación
2. **Operaciones** → Monitoreo, priorización, llamado de camiones  
3. **Portería Ingreso** → Control acceso, verificación documental
4. **Playa Precalado** → Organización FIFO por cereal
5. **Calada** → Inspección, análisis calidad, clasificación
6. **Playa Post-Calada** → Ordenamiento por calidad + FIFO
7. **Báscula Bruto** → Registro peso bruto, asignación plataforma
8. **Plataformas Descarga** → Descarga mercadería por cereal/calidad
9. **Báscula Tara** → Peso final, cálculo neto, emisión ticket
10. **Portería Salida** → Control egreso, cierre carta porte

## Patrones de Desarrollo Específicos

### Integración ARCA/AFIP Multi-Servicio
- **3 Servicios ARCA**: CPE (Cartas Porte), EMBARQUES (Comunicaciones), FACTURACION (Electrónica)
- **Certificados SSL específicos** por servicio desde `.env` (ARCA_CPE_*, ARCA_EMBARQUES_*, etc.)
- **Función parameterless**: `get_arca_access_ticket()` lee configuración automáticamente desde `.env`
- **OpenSSL CLI signing**: Firma CMS usando subprocess calls (compatible con protocolo AFIP)
- **Timezone GMT-3** (Argentina) en `TIMEZONE_OFFSET = -3`
- **XML TRA generación**: Timestamps ISO 8601 para cada servicio específico

### Modelos SQLModel
- Usa **SQLModel** (no SQLAlchemy puro) para compatibilidad FastAPI + ORM
- Implementa relaciones many-to-many con tabla intermedia explícita:
```python
# Patrón: Tabla de relación con back_populates
User_Item_Relation(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    
User.items = Relationship(back_populates="user", link_model=User_Item_Relation)
```

### Convenciones de Naming
- **Español para campos de negocio**: `nombre_completo`, `habilitado`, `regimen`  
- **Inglés para infraestructura**: `id`, `username`, `email`
- **Sectores numerados**: Playa3.1, Operaciones3.2, etc. según documentación
- **Estados de camión**: "En Viaje", "Ingresado", "En Calada", "Descargando", "Salido"

## Comandos de Desarrollo Críticos

### Entorno Virtual
```powershell
# Activación (ya configurado en terminal)
.\venv\Scripts\Activate.ps1

# Instalar dependencias ARCA/SSL
pip install fastapi uvicorn pyopenssl cryptography zeep lxml sqlmodel python-dotenv
```

### Testing HTTP
- **API corriendo en**: `http://127.0.0.1:8080` (puerto actualizado)
- **Endpoints disponibles**:
  - `GET /get-ticket` - Token ARCA (CPE por defecto)
  - `GET /get-ticket-cpe` - Token Cartas de Porte Electrónica
  - `GET /get-ticket-embarques` - Token Comunicaciones de Embarques
  - `GET /get-ticket-facturacion` - Token Facturación Electrónica
  - `GET /diagnose-certs` - Diagnóstico certificados SSL multi-servicio
  - `GET /docs` - Documentación Swagger automática
- **Validar respuesta**: `"status": "success"` con datos específicos del servicio

### Gestión Certificados Multi-Servicio
```python
# CONFIGURACIÓN .ENV POR SERVICIO:
# ARCA_CPE_CERT_FILE, ARCA_CPE_KEY_FILE, ARCA_CPE_SERVICE_NAME
# ARCA_EMBARQUES_CERT_FILE, ARCA_EMBARQUES_KEY_FILE, ARCA_EMBARQUES_SERVICE_NAME  
# ARCA_FACTURACION_CERT_FILE, ARCA_FACTURACION_KEY_FILE, ARCA_FACTURACION_SERVICE_NAME

# FUNCIÓN AUTOMÁTICA: Lee configuración desde .env
result = get_arca_access_ticket()  # CPE por defecto
result = get_arca_access_ticket("EMBARQUES")  # Servicio específico

# NO commitear certificados ni .env (ver .gitignore)
```

## Documentación de Referencia

### Historias de Usuario
- [historias_de_usuario.md](Diagramas%20y%20Documentos%20Varios/historias_de_usuario.md) - Casos de uso por sector operativo
- [sistema_terminal_portuaria.md](Diagramas%20y%20Documentos%20Varios/sistema_terminal_portuaria.md) - Especificación completa (284 líneas)
- [Mapa UML.puml](Diagramas%20y%20Documentos%20Varios/Mapa%20UML.puml) - Modelo de datos contractual (Puerto→Empresa→Cereal→Contrato→Cupo)

### Reglas de Negocio Críticas
- **FIFO por cereal**: Orden temporal dentro de cada tipo de grano
- **Prioridad por calidad**: Post-calada ordena por calidad antes que FIFO
- **Validación ARCA obligatoria**: Sin QR válido no hay ingreso a playa
- **Trazabilidad completa**: Cada escaneado QR actualiza estado en BD
- **Tolerancia de peso**: Sistema detecta diferencias bruto-tara vs carta porte

### Integraciones Externas
- **ARCA (AFIP)**: Validación cartas de porte mediante WSAA + SOAP
- **Báscula**: Interfaces peso bruto/tara (implementar según hardware)  
- **QR Scanning**: Lectura carta porte para trazabilidad camión

## Notas de Implementación

Al trabajar con este proyecto, prioriza la **trazabilidad de estados** y **integridad de flujo operativo**. Cada modificación debe considerar el impacto en los 10 sectores interconectados y mantener compatibilidad con protocolos ARCA/AFIP existentes.

## Estado Actual de Implementación (Diciembre 2025)

### ✅ Completado
- **ARCA Multi-Servicio**: 3 servicios implementados (CPE, EMBARQUES, FACTURACION)
- **Endpoints FastAPI**: 7 endpoints funcionales en puerto 8080
- **Configuración .env**: Variables por servicio, funciones parameterless
- **Certificados SSL**: Validación y carga automática por servicio
- **OpenSSL CLI**: Firma CMS compatible con protocolo AFIP
- **Documentación Swagger**: Auto-generada en `/docs`

### 🔄 Estado Operativo
- **API Running**: `http://127.0.0.1:8080` con hot reload
- **Certificados**: Validados y funcionales para testing
- **Logging**: Configurado para troubleshooting ARCA
- **Environment**: Python venv activado con todas las dependencias

### 📋 Próximos Pasos Sugeridos
- Implementar endpoints de negocio (sectores 1-10)
- Integrar base de datos SQLModel para trazabilidad camiones
- Desarrollar interfaces QR scanning y báscula
- Configurar producción con certificados AFIP reales