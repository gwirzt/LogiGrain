# Sistema de Logging - LogiGrain

## 📝 Descripción

La carpeta `logs/` contiene el sistema de logging centralizado de LogiGrain que registra todas las operaciones del sistema, especialmente las transacciones ARCA/AFIP y operaciones de la API.

## 📁 Archivos

### `logigrain.log`
- **Archivo principal** de logs en producción
- Contiene registro completo de operaciones del sistema
- **Rotación automática** configurada para manejo eficiente

### Archivos de rotación (automáticos)
- `logigrain.log.1` - Primera rotación (más reciente)
- `logigrain.log.2` - Segunda rotación 
- `...`
- `logigrain.log.10` - Décima rotación (más antigua)

## ⚙️ Configuración de Rotación

### Parámetros configurados:
- **Tamaño máximo por archivo:** 5MB
- **Archivos históricos mantenidos:** 10 archivos
- **Encoding:** UTF-8 (soporte completo para caracteres especiales)
- **Clase utilizada:** `RotatingFileHandler` de Python

### ¿Cómo funciona la rotación?
1. Cuando `logigrain.log` llega a **5MB**, se renombra a `logigrain.log.1`
2. Se crea un nuevo `logigrain.log` limpio
3. Las rotaciones previas se mueven: `.1` → `.2`, `.2` → `.3`, etc.
4. Se mantienen **máximo 10 archivos** históricos
5. El archivo `.10` se elimina automáticamente cuando se genera una nueva rotación

## 🏗️ Sistema de Logging Centralizado

### Ubicación del código
**Configuración principal:** [`utils/logger.py`](../utils/logger.py)

### Loggers configurados:

#### Logger `main` 
- **Origen:** [`main.py`](../main.py)
- **Registra:** Operaciones de endpoints, inicio de servidor, diagnósticos
- **Formato:** `2025-12-29 18:49:43 - main - INFO - Mensaje`

#### Logger `arca`
- **Origen:** [`Arca/wsaa.py`](../Arca/wsaa.py) 
- **Registra:** Todas las operaciones ARCA/AFIP:
  - Validación de certificados SSL
  - Generación de TRA (Ticket Request Authentication)
  - Firma CMS con OpenSSL
  - Llamadas WSAA (Web Service Authentication and Authorization)
  - Tokens y errores de autenticación
- **Formato:** `2025-12-29 18:49:43 - arca - INFO - Mensaje`

## 📋 Tipos de Operaciones Registradas

### Operaciones ARCA/AFIP (Logger `arca`)
- ✅ **Autenticación exitosa** - Token obtenido correctamente
- ⚠️ **Validación certificados** - Estado de certificados SSL
- 🔧 **Procesos OpenSSL** - Firma CMS y comandos ejecutados
- 🌐 **Llamadas WSAA** - Comunicación con servicios AFIP
- ❌ **Errores ARCA** - Fallos en autenticación o conectividad

### Operaciones API (Logger `main`)
- 🚀 **Inicio endpoints** - Solicitudes de tokens específicos
- 🔍 **Diagnósticos** - Verificaciones de certificados y sistema
- ⚡ **Health checks** - Estado general del sistema
- ❌ **Errores HTTP** - Fallos en endpoints

## 🔧 Configuración Técnica

### Formato de mensaje estándar:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Niveles de logging utilizados:
- **INFO** - Operaciones normales y flujos exitosos
- **WARNING** - Situaciones que requieren atención pero no son críticas  
- **ERROR** - Errores que impiden operaciones específicas
- **DEBUG** - Información detallada para desarrollo (opcional)

### Salidas configuradas:
1. **Consola** (`StreamHandler`) - Para monitoreo en tiempo real
2. **Archivo** (`RotatingFileHandler`) - Para persistencia y auditoría

## 🎯 Casos de Uso

### Para Desarrollo
- **Debugging ARCA:** Ver flujo completo de autenticación AFIP
- **Testing endpoints:** Verificar respuestas y errores de API
- **Troubleshooting:** Identificar problemas de certificados o conectividad

### Para Operaciones
- **Auditoría:** Registro completo de tokens solicitados y por quién
- **Monitoreo:** Estado de servicios ARCA/AFIP en tiempo real
- **Resolución de incidentes:** Trazabilidad completa de errores

### Para Administración
- **Análisis de uso:** Frecuencia de solicitudes por servicio
- **Capacidad:** Control de crecimiento de archivos con rotación automática
- **Compliance:** Mantenimiento de registros históricos

## 📊 Ejemplo de Trazabilidad Completa

### Flujo de token CPE típico:
```log
2025-12-29 18:49:43 - main - INFO - Solicitud token CPE
2025-12-29 18:49:43 - arca - INFO - Iniciando autenticación ARCA - Tipo: 'CPE'
2025-12-29 18:49:43 - arca - INFO - Configuración obtenida: servicio=wscpe
2025-12-29 18:49:43 - arca - INFO - Validación de certificados completada
2025-12-29 18:49:43 - arca - INFO - Creando TRA para servicio: wscpe
2025-12-29 18:49:43 - arca - INFO - TRA XML generado exitosamente
2025-12-29 18:49:43 - arca - INFO - Firmando TRA con OpenSSL CLI
2025-12-29 18:49:43 - arca - INFO - OpenSSL ejecutado exitosamente
2025-12-29 18:49:43 - arca - INFO - CMS generado, longitud: 2324
2025-12-29 18:49:43 - arca - INFO - Llamando WSAA: https://wsaa.afip.gov.ar/ws/services/LoginCms
2025-12-29 18:49:44 - arca - INFO - Respuesta WSAA recibida exitosamente
2025-12-29 18:49:44 - arca - INFO - Token y Sign extraídos exitosamente
2025-12-29 18:49:44 - arca - INFO - Autenticación ARCA completada exitosamente
```

## 🔄 Mantenimiento

### Rotación automática
- **No requiere intervención manual**
- Los archivos se rotan automáticamente al alcanzar 5MB
- El sistema mantiene automáticamente 10 versiones históricas

### Limpieza manual (opcional)
```powershell
# Limpiar log actual (mantener rotaciones)
Clear-Content logs\logigrain.log

# Eliminar todas las rotaciones (inicio limpio)
Remove-Item logs\logigrain.log.* -Force
```

---

**Configurado:** 29 de diciembre de 2025  
**Sistema:** LogiGrain v1.0.0 - Terminal Portuaria  
**Integración:** ARCA/AFIP Multi-Servicio (CPE, EMBARQUES, FACTURACIÓN)