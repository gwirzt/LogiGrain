# Base de Datos y Modelos - LogiGrain

## 🗄️ Descripción General

LogiGrain utiliza SQLite como base de datos principal con SQLModel como ORM, proporcionando una arquitectura de datos robusta y escalable para la gestión integral de terminales portuarias.

## 🏗️ Arquitectura de Base de Datos

### Motor de Base de Datos
- **Tecnología**: SQLite 3.x
- **ORM**: SQLModel (FastAPI + SQLAlchemy 2.0)
- **Archivo**: `logigrain.db` en raíz del proyecto
- **Conexión**: Thread-safe con pooling automático

### Configuración de Conexión
```python
# main.py
DATABASE_URL = "sqlite:///./logigrain.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    """Dependency para obtener sesión de base de datos"""
    with Session(engine) as session:
        yield session
```

## 📊 Modelo de Datos Completo

### Diagrama de Relaciones

```mermaid
erDiagram
    Usuario ||--o{ UsuarioPuerto : "tiene acceso"
    Puerto ||--o{ UsuarioPuerto : "permite acceso"
    Usuario ||--o{ ArcaToken : "posee"
    Puerto ||--o{ ArcaToken : "específico"
    
    Usuario {
        int id PK
        string username UK
        string password_hash
        string nombre_completo
        string email UK
        boolean habilitado
        boolean es_admin
        datetime fecha_creacion
        datetime ultimo_acceso
    }
    
    Puerto {
        int id PK
        string nombre
        string codigo UK
        string descripcion
        string ubicacion
        boolean habilitado
        datetime fecha_creacion
    }
    
    UsuarioPuerto {
        int usuario_id PK,FK
        int puerto_id PK,FK
        datetime fecha_asignacion
        boolean habilitado
    }
    
    ArcaToken {
        int id PK
        int usuario_id FK
        string puerto_codigo
        string servicio_tipo
        text token
        string sign
        datetime fecha_solicitud
        datetime fecha_vencimiento
        string wsaa_url
        string servicio_nombre
    }
    
    Item {
        int id PK
        string title
        string description
        boolean habilitado
    }
```

## 🏛️ Tablas Principales

### 1. Tabla `usuario`

```sql
CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    habilitado BOOLEAN DEFAULT 1,
    es_admin BOOLEAN DEFAULT 0,
    fecha_creacion DATETIME DEFAULT (datetime('now', 'utc')),
    ultimo_acceso DATETIME
);

-- Índices
CREATE INDEX ix_usuario_username ON usuario (username);
CREATE INDEX ix_usuario_email ON usuario (email);
```

**Propósito**: Gestión de usuarios del sistema con autenticación y permisos.

**Características**:
- Username único para login
- Password hasheado con SHA-256
- Control de habilitación por usuario
- Tracking de último acceso

### 2. Tabla `puerto`

```sql
CREATE TABLE puerto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    descripcion VARCHAR(255),
    ubicacion VARCHAR(255),
    habilitado BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT (datetime('now', 'utc'))
);

-- Índices
CREATE INDEX ix_puerto_codigo ON puerto (codigo);
```

**Propósito**: Definición de terminales portuarias de la empresa.

**Características**:
- Código único por puerto (TRP1, TRP2, TSL1)
- Información descriptiva y geográfica
- Control de estado operativo

### 3. Tabla `usuariopuerto` (Relación Many-to-Many)

```sql
CREATE TABLE usuariopuerto (
    usuario_id INTEGER NOT NULL,
    puerto_id INTEGER NOT NULL,
    fecha_asignacion DATETIME DEFAULT (datetime('now', 'utc')),
    habilitado BOOLEAN DEFAULT 1,
    PRIMARY KEY (usuario_id, puerto_id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id),
    FOREIGN KEY (puerto_id) REFERENCES puerto(id)
);

-- Índices
CREATE INDEX ix_usuariopuerto_usuario_id ON usuariopuerto (usuario_id);
CREATE INDEX ix_usuariopuerto_puerto_id ON usuariopuerto (puerto_id);
```

**Propósito**: Gestión de permisos de acceso de usuarios a puertos específicos.

**Características**:
- Relación many-to-many entre usuarios y puertos
- Control de habilitación por asignación
- Fecha de asignación para auditoría

### 4. Tabla `arca_tokens` (Sistema de Cache)

```sql
CREATE TABLE arca_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    puerto_codigo VARCHAR(10) NOT NULL,
    servicio_tipo VARCHAR(20) NOT NULL,
    token TEXT(2000) NOT NULL,
    sign VARCHAR(1000) NOT NULL,
    fecha_solicitud DATETIME DEFAULT (datetime('now', 'utc')),
    fecha_vencimiento DATETIME NOT NULL,
    wsaa_url VARCHAR(200),
    servicio_nombre VARCHAR(50),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Índices optimizados para cache
CREATE INDEX ix_arca_tokens_lookup ON arca_tokens 
(usuario_id, puerto_codigo, servicio_tipo, fecha_vencimiento);

CREATE INDEX ix_arca_tokens_expiry ON arca_tokens (fecha_vencimiento);
```

**Propósito**: Cache inteligente para tokens ARCA/AFIP por usuario y puerto.

**Características**:
- Cache triplex: usuario + puerto + servicio
- Expiración automática (8 horas)
- Optimización de consultas ARCA/AFIP

### 5. Tabla `item` (Legacy)

```sql
CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR NOT NULL,
    description VARCHAR,
    habilitado BOOLEAN DEFAULT 1
);
```

**Propósito**: Tabla legacy mantenida por compatibilidad.

## 🔧 Modelos SQLModel

### Arquitectura de Modelos

```python
# Modelos/usuario.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
```

### Modelo Base Usuario

```python
class Usuario(SQLModel, table=True):
    """Modelo principal para usuarios del sistema"""
    id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    nombre_completo: str = Field(max_length=150)
    email: str = Field(max_length=100, unique=True, index=True)
    habilitado: bool = Field(default=True)
    es_admin: bool = Field(default=False)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    ultimo_acceso: Optional[datetime] = Field(default=None)
    
    # Relaciones
    puertos: List["UsuarioPuerto"] = Relationship(back_populates="usuario")
    arca_tokens: List["ArcaToken"] = Relationship(back_populates="usuario")
    
    def set_password(self, password: str) -> None:
        """Hashea y establece la contraseña"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
```

### Modelo Puerto

```python
class Puerto(SQLModel, table=True):
    """Modelo para terminales portuarias"""
    id: int = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    codigo: str = Field(max_length=10, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    ubicacion: Optional[str] = Field(default=None, max_length=255)
    habilitado: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    
    # Relación con usuarios
    usuarios: List["UsuarioPuerto"] = Relationship(back_populates="puerto")
```

### Modelo de Relación

```python
class UsuarioPuerto(SQLModel, table=True):
    """Tabla de relación Usuario-Puerto (Many-to-Many)"""
    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    puerto_id: int = Field(foreign_key="puerto.id", primary_key=True)
    fecha_asignacion: datetime = Field(default_factory=datetime.utcnow)
    habilitado: bool = Field(default=True)
    
    # Relaciones bidireccionales
    usuario: Usuario = Relationship(back_populates="puertos")
    puerto: Puerto = Relationship(back_populates="usuarios")
```

### Modelo Cache ARCA

```python
class ArcaToken(SQLModel, table=True):
    """Modelo para cache de tokens ARCA/AFIP"""
    __tablename__ = "arca_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    puerto_codigo: str = Field(max_length=10, index=True)
    servicio_tipo: str = Field(max_length=20, index=True)
    token: str = Field(max_length=2000)
    sign: str = Field(max_length=1000)
    fecha_solicitud: datetime = Field(default_factory=datetime.utcnow)
    fecha_vencimiento: datetime
    wsaa_url: Optional[str] = Field(default=None, max_length=200)
    servicio_nombre: Optional[str] = Field(default=None, max_length=50)
    
    # Relación con usuario
    usuario: "Usuario" = Relationship(back_populates="arca_tokens")
    
    def is_expired(self) -> bool:
        """Verificar si el token ha expirado"""
        return datetime.utcnow() >= self.fecha_vencimiento
```

## 🎯 DTOs (Data Transfer Objects)

### Request Models

```python
class UsuarioLogin(SQLModel):
    """Modelo para request de login"""
    username: str
    password: str

class ArcaTokenRequest(SQLModel):
    """Request model para solicitudes de token ARCA"""
    puerto_codigo: str = Field(..., min_length=3, max_length=10)
```

### Response Models

```python
class UsuarioResponse(SQLModel):
    """Usuario sin información sensible"""
    id: int
    username: str
    nombre_completo: str
    email: str
    habilitado: bool
    es_admin: bool
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime]

class PuertoResponse(SQLModel):
    """Información completa del puerto"""
    id: int
    nombre: str
    codigo: str
    descripcion: Optional[str]
    ubicacion: Optional[str]
    habilitado: bool

class LoginResponse(SQLModel):
    """Respuesta completa de login"""
    usuario: UsuarioResponse
    puertos: List[PuertoResponse]
    token: str
    mensaje: str
```

## 🔄 Gestión de Sesiones

### Dependency Injection Pattern

```python
def get_session():
    """FastAPI dependency para sesiones de BD"""
    with Session(engine) as session:
        yield session

# Uso en endpoints
@app.post("/login")
async def login(
    user_credentials: UsuarioLogin,
    session: Session = Depends(get_session)  # <- Dependency injection
):
```

### Operaciones CRUD Típicas

#### Create (Insertar)
```python
def create_user(user_data: dict, session: Session):
    new_user = Usuario(
        username=user_data["username"],
        nombre_completo=user_data["nombre_completo"],
        email=user_data["email"]
    )
    new_user.set_password(user_data["password"])
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
```

#### Read (Consultar)
```python
def get_user_by_username(username: str, session: Session):
    statement = select(Usuario).where(Usuario.username == username)
    return session.exec(statement).first()

def get_user_puertos(user_id: int, session: Session):
    statement = select(UsuarioPuerto, Puerto).join(Puerto).where(
        UsuarioPuerto.usuario_id == user_id,
        UsuarioPuerto.habilitado == True
    )
    return session.exec(statement).all()
```

#### Update (Actualizar)
```python
def update_last_access(user_id: int, session: Session):
    statement = select(Usuario).where(Usuario.id == user_id)
    user = session.exec(statement).first()
    
    if user:
        user.ultimo_acceso = datetime.utcnow()
        session.add(user)
        session.commit()
```

#### Delete (Eliminar)
```python
def delete_expired_tokens(session: Session):
    statement = select(ArcaToken).where(
        ArcaToken.fecha_vencimiento < datetime.utcnow()
    )
    expired_tokens = session.exec(statement).all()
    
    for token in expired_tokens:
        session.delete(token)
    
    session.commit()
```

## 🚀 Inicialización de Base de Datos

### Script `init_db.py`

El script de inicialización crea automáticamente:

1. **Estructura de tablas**: Usando SQLModel.metadata.create_all()
2. **Puertos predefinidos**: TRP1, TRP2, TSL1
3. **Usuarios de prueba**: admin, operador1, supervisor, gerente
4. **Asignaciones de permisos**: Relaciones usuario-puerto

```python
def create_db_and_tables():
    """Crear base de datos y tablas si no existen"""
    try:
        SQLModel.metadata.create_all(engine, checkfirst=True)
    except Exception as e:
        logger.warning(f"Las tablas ya existen: {e}")

# Datos de inicialización
puertos_iniciales = [
    {
        "nombre": "Terminal Rosario Puerto 1",
        "codigo": "TRP1",
        "descripcion": "Terminal principal de cereales",
        "ubicacion": "Puerto de Rosario - Zona Norte"
    },
    # ... más puertos
]

usuarios_iniciales = [
    {
        "username": "admin",
        "password": "admin123",
        "nombre_completo": "Administrador Principal",
        "email": "admin@logigrain.com",
        "es_admin": True
    },
    # ... más usuarios
]
```

## 📊 Optimización y Performance

### Índices Estratégicos

```python
# Índices más utilizados
"""
1. ix_usuario_username - Login frecuente
2. ix_arca_tokens_lookup - Cache ARCA triplex
3. ix_arca_tokens_expiry - Limpieza de expirados
4. ix_usuariopuerto_usuario_id - Permisos por usuario
"""
```

### Query Optimization

```python
# Usar select() específico en lugar de query all
statement = select(Usuario.id, Usuario.username).where(
    Usuario.habilitado == True
)

# Joins optimizados para relaciones
statement = select(UsuarioPuerto, Puerto).join(Puerto).where(
    UsuarioPuerto.usuario_id == user_id
)

# Limit para paginación
statement = select(ArcaToken).limit(100).offset(page * 100)
```

### Connection Pooling

```python
# Configuración optimizada del engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,  # Verificar conexiones
    pool_recycle=300,    # Reciclar cada 5 minutos
    echo=False           # Disable SQL logging en producción
)
```

## 🔄 Migraciones y Versionado

### Estrategia de Migraciones

```python
# Futuras migraciones con Alembic
"""
alembic init alembic
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
"""

# Por ahora: SQLModel.metadata.create_all() handles schema
def migrate_schema():
    """Migración automática de schema"""
    SQLModel.metadata.create_all(engine, checkfirst=True)
    logger.info("Schema migrado exitosamente")
```

### Backup y Restore

```python
def backup_database():
    """Backup de SQLite"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/logigrain_backup_{timestamp}.db"
    
    shutil.copy2("logigrain.db", backup_file)
    logger.info(f"Backup creado: {backup_file}")
```

## 🧪 Testing de Base de Datos

### Test Database

```python
# conftest.py para testing
import pytest
from sqlmodel import create_engine, Session

@pytest.fixture
def test_session():
    """Sesión de BD para testing"""
    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        yield session
```

### Test Cases

```python
def test_user_creation(test_session):
    """Test creación de usuario"""
    user = Usuario(
        username="test_user",
        nombre_completo="Test User",
        email="test@example.com"
    )
    user.set_password("test123")
    
    test_session.add(user)
    test_session.commit()
    
    assert user.id is not None
    assert user.verify_password("test123")

def test_user_puerto_relationship(test_session):
    """Test relación usuario-puerto"""
    # Crear usuario y puerto
    user = Usuario(username="test", ...)
    puerto = Puerto(codigo="TEST", nombre="Test Port")
    
    test_session.add_all([user, puerto])
    test_session.commit()
    
    # Crear relación
    relacion = UsuarioPuerto(usuario_id=user.id, puerto_id=puerto.id)
    test_session.add(relacion)
    test_session.commit()
    
    # Verificar relación
    statement = select(UsuarioPuerto).where(UsuarioPuerto.usuario_id == user.id)
    result = test_session.exec(statement).first()
    
    assert result is not None
    assert result.puerto_id == puerto.id
```

## 🔒 Seguridad de Base de Datos

### Medidas Implementadas

1. **Prepared Statements**: SQLAlchemy previene SQL injection
2. **Password Hashing**: SHA-256 (mejorable a bcrypt)
3. **Connection Security**: SQLite local, sin acceso remoto
4. **Session Management**: Transacciones automáticas

### Recomendaciones para Producción

```python
# 1. Migrar a PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/logigrain"

# 2. Encriptación a nivel de columna
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str) -> str:
    key = os.getenv("ENCRYPTION_KEY")
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

# 3. Audit logging
class AuditLog(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    action: str
    table_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

## 📚 Referencias

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/) - ORM oficial
- [SQLAlchemy 2.0 Guide](https://docs.sqlalchemy.org/en/20/) - Core engine
- [SQLite Documentation](https://sqlite.org/docs.html) - Base de datos
- [Alembic](https://alembic.sqlalchemy.org/) - Migraciones de schema
- [FastAPI Database](https://fastapi.tiangolo.com/tutorial/sql-databases/) - Integración oficial