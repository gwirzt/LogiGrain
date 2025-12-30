# Login y Autenticación JWT - LogiGrain

## 🔐 Descripción General

El sistema de autenticación de LogiGrain implementa JWT (JSON Web Tokens) para proporcionar autenticación segura y stateless. Los usuarios se autentican una vez y reciben un token válido por 8 horas que les permite acceder a todos los endpoints protegidos.

## 🏗️ Arquitectura

### Componentes Principales

1. **Endpoint de Login** (`POST /login`)
2. **Funciones de Validación JWT**
3. **Middleware de Autenticación**
4. **Sistema de Permisos por Puerto**

### Flujo de Autenticación

```mermaid
graph TD
    A[Cliente] -->|POST /login| B[Validar Credenciales]
    B -->|Válidas| C[Consultar Puertos del Usuario]
    B -->|Inválidas| D[HTTP 401]
    C --> E[Generar Token JWT]
    E --> F[Retornar Usuario + Puertos + Token]
    F --> G[Cliente guarda token]
    G -->|Requests posteriores| H[Bearer Token en Header]
    H --> I[Validar Token]
    I -->|Válido| J[Acceso Permitido]
    I -->|Inválido/Expirado| K[HTTP 401]
```

## 🔧 Implementación Técnica

### Configuración JWT

```python
# Configuración en main.py
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "logigrain-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas
```

### Estructura del Token JWT

```json
{
  "sub": "admin",           // Username
  "user_id": 1,            // ID del usuario
  "is_admin": true,        // Si es administrador
  "puertos": ["TRP1", "TRP2", "TSL1"], // Códigos de puertos
  "exp": 1735589234        // Timestamp de expiración
}
```

### Funciones Principales

#### 1. `create_access_token()`
Crea un nuevo token JWT con la información del usuario.

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### 2. `verify_token()`
Verifica y decodifica el token JWT del header Authorization.

```python
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        # ... validaciones adicionales
        return token_data
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
```

#### 3. `get_current_user()`
Obtiene el usuario actual desde la base de datos usando la información del token.

## 📋 Endpoint de Login

### Request
```http
POST /login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

### Response Exitosa
```json
{
  "usuario": {
    "id": 1,
    "username": "admin",
    "nombre_completo": "Administrador Principal",
    "email": "admin@logigrain.com",
    "habilitado": true,
    "es_admin": true,
    "fecha_creacion": "2025-12-30T20:53:07.123456",
    "ultimo_acceso": "2025-12-30T20:53:08.654321"
  },
  "puertos": [
    {
      "id": 1,
      "nombre": "Terminal Rosario Puerto 1",
      "codigo": "TRP1",
      "descripcion": "Terminal principal de cereales",
      "ubicacion": "Puerto de Rosario - Zona Norte",
      "habilitado": true
    }
  ],
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "mensaje": "Login exitoso. Acceso a 3 puerto(s)."
}
```

### Errores Comunes

| Código | Error | Causa |
|--------|-------|-------|
| 401 | Credenciales inválidas | Username no existe o password incorrecto |
| 403 | Usuario deshabilitado | Usuario existe pero está desactivado |
| 403 | Usuario sin puertos asignados | Usuario válido pero sin acceso a ningún puerto |

## 🔒 Uso del Token

### En Headers HTTP
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Validación Automática
Todos los endpoints protegidos usan el dependency `get_current_user()`:

```python
@app.post("/get-ticket-cpe")
async def get_ticket_cpe(
    request: ArcaTokenRequest,
    current_user: Usuario = Depends(get_current_user)  # <- Validación automática
):
```

## 👥 Usuarios de Prueba

| Username | Password | Rol | Acceso a Puertos |
|----------|----------|-----|------------------|
| admin | admin123 | Administrador | Todos los puertos |
| operador1 | op123 | Operador | TRP1, TRP2 |
| supervisor | super123 | Supervisor | TRP2, TSL1 |
| gerente | ger123 | Gerente | TSL1 |

## 📊 Logging de Autenticación

### Eventos Registrados
- ✅ **Login exitoso**: Usuario, puertos asignados
- ❌ **Login fallido**: Usuario no encontrado, contraseña incorrecta
- ⚠️ **Usuario deshabilitado**: Intento de acceso con usuario inactivo
- 🔒 **Token inválido**: Intentos con tokens expirados o malformados

### Formato de Logs
```
2025-12-30 18:28:08 - main - INFO - Intento de login para usuario: admin
2025-12-30 18:28:08 - main - INFO - Login exitoso para usuario: admin
2025-12-30 18:28:08 - main - WARNING - Login fallido para usuario: operador99 - Usuario no encontrado
```

## 🛡️ Seguridad

### Medidas Implementadas
- **Hash de contraseñas**: SHA-256 (mejorable a bcrypt en producción)
- **Tokens JWT firmados**: Algoritmo HS256
- **Expiración automática**: 8 horas
- **Validación en cada request**: Verificación automática del token
- **Logging completo**: Auditoría de todos los intentos de acceso

### Recomendaciones para Producción
1. **Cambiar SECRET_KEY**: Usar una clave segura de 32+ caracteres
2. **Usar HTTPS**: Siempre en producción
3. **Implementar refresh tokens**: Para renovación automática
4. **Rate limiting**: Prevenir ataques de fuerza bruta
5. **Hash más seguro**: bcrypt o Argon2 en lugar de SHA-256

## 🔧 Configuración

### Variables de Entorno
```env
# JWT Configuration
JWT_SECRET_KEY=logigrain-secret-key-change-in-production-2024
```

### Duración del Token
Para cambiar la duración del token, modifica en `main.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # Cambiar según necesidades
```

## 🧪 Testing

### Login Correcto
```bash
curl -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Usar Token en Request
```bash
curl -X POST http://127.0.0.1:8080/get-ticket-cpe \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"puerto_codigo": "TRP1"}'
```

## 📚 Referencias

- [JWT.io](https://jwt.io/) - Información sobre JSON Web Tokens
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) - Documentación oficial
- [python-jose](https://python-jose.readthedocs.io/) - Librería JWT usada