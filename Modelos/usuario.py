from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
import hashlib


# === MODELOS DE NEGOCIO === #

class Puerto(SQLModel, table=True):
    """Modelo para puertos/unidades de negocio"""
    id: int = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    codigo: str = Field(max_length=10, unique=True)  # Ej: "TRP1", "TRP2"
    descripcion: Optional[str] = Field(default=None, max_length=255)
    ubicacion: Optional[str] = Field(default=None, max_length=255)
    habilitado: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    
    # Relación con usuarios
    usuarios: List["UsuarioPuerto"] = Relationship(back_populates="puerto")


class Usuario(SQLModel, table=True):
    """Modelo para usuarios del sistema"""
    id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    password_hash: str = Field(max_length=255)  # Hash de la contraseña
    nombre_completo: str = Field(max_length=150)
    email: str = Field(max_length=100, unique=True, index=True)
    habilitado: bool = Field(default=True)
    es_admin: bool = Field(default=False)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    ultimo_acceso: Optional[datetime] = Field(default=None)
    
    # Relación con puertos
    puertos: List["UsuarioPuerto"] = Relationship(back_populates="usuario")
    
    # Relación con tokens ARCA
    arca_tokens: List["ArcaToken"] = Relationship(back_populates="usuario")
    
    def set_password(self, password: str) -> None:
        """Hashea y establece la contraseña"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


class UsuarioPuerto(SQLModel, table=True):
    """Tabla de relación Usuario-Puerto (Many-to-Many)"""
    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    puerto_id: int = Field(foreign_key="puerto.id", primary_key=True)
    fecha_asignacion: datetime = Field(default_factory=datetime.utcnow)
    habilitado: bool = Field(default=True)
    
    # Relaciones
    usuario: Usuario = Relationship(back_populates="puertos")
    puerto: Puerto = Relationship(back_populates="usuarios")


# === MODELOS DE RESPUESTA (DTOs) === #

class UsuarioLogin(SQLModel):
    """Modelo para request de login"""
    username: str
    password: str


class UsuarioResponse(SQLModel):
    """Modelo para respuesta de usuario (sin contraseña)"""
    id: int
    username: str
    nombre_completo: str
    email: str
    habilitado: bool
    es_admin: bool
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime]


class PuertoResponse(SQLModel):
    """Modelo para respuesta de puerto"""
    id: int
    nombre: str
    codigo: str
    descripcion: Optional[str]
    ubicacion: Optional[str]
    habilitado: bool


class LoginResponse(SQLModel):
    """Modelo para respuesta de login exitoso"""
    usuario: UsuarioResponse
    puertos: List[PuertoResponse]
    token: str
    mensaje: str


# === MODELOS LEGACY (mantener por compatibilidad) === #

class Item(SQLModel, table=True):
    """Modelo legacy - mantener por compatibilidad"""
    id: int = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    habilitado: bool = True 

