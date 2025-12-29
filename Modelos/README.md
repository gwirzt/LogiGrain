# Modelos - Esquemas de Datos del Sistema

## Propósito del Módulo

El módulo **Modelos** define todos los esquemas de datos utilizados en el sistema LogiGrain usando **SQLModel**, proporcionando una capa de abstracción entre la base de datos y la API que es compatible tanto con FastAPI como con ORM de SQLAlchemy.

## Componentes del Módulo

### Archivos de Esquemas
- `usuario.py` - Modelos de usuarios, items y relaciones
- `carta_porte.py` - Esquemas de cartas de porte electrónicas  
- `arca_responses.py` - Modelos de respuestas de servicios ARCA/AFIP

## Arquitectura SQLModel

### Características Técnicas
- **SQLModel**: Framework híbrido FastAPI + SQLAlchemy ORM
- **Tipado fuerte**: Type hints completos para validación automática
- **Pydantic integration**: Validación automática de datos de entrada
- **Auto-documentation**: Esquemas automáticos en Swagger/OpenAPI

### Convenciones de Naming
```python
# Campos de negocio en español
nombre_completo: str
habilitado: bool
regimen: str

# Campos de infraestructura en inglés  
id: int
username: str
email: str
created_at: datetime
```

## Modelos de Usuarios y Autenticación

### Usuario Base
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True)
    nombre_completo: str = Field(max_length=200)
    habilitado: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    items: List["Item"] = Relationship(back_populates="user", link_model=User_Item_Relation)
```

### Roles y Permisos
```python
class UserRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  
    user_id: int = Field(foreign_key="user.id")
    role: str = Field(max_length=50)  # "admin", "operador", "supervisor"
    sector: Optional[str] = Field(max_length=100)  # Sector específico
```

## Modelos de Operaciones

### Camión y Transporte
```python
class Camion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patente: str = Field(unique=True, max_length=10)
    modelo: Optional[str] = Field(max_length=100)
    año: Optional[int] = None
    capacidad_kg: Optional[float] = None
    empresa_transporte_id: int = Field(foreign_key="empresatransporte.id")
    habilitado: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Chofer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cuit: str = Field(unique=True, max_length=11)
    nombre_completo: str = Field(max_length=200)
    dni: str = Field(unique=True, max_length=8)
    registro_conductor: str = Field(max_length=20)
    habilitado: bool = Field(default=True)
    vencimiento_registro: Optional[date] = None
```

### Empresa y Contratos
```python
class Empresa(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cuit: str = Field(unique=True, max_length=11)
    razon_social: str = Field(max_length=200)
    habilitada: bool = Field(default=True)
    regimen: str = Field(max_length=50)  # "EXPORTACION", "MERCADO_INTERNO"
    
    # Relaciones
    contratos: List["Contrato"] = Relationship(back_populates="empresa")

class Contrato(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(unique=True, max_length=50)
    empresa_id: int = Field(foreign_key="empresa.id")
    cereal: str = Field(max_length=50)
    cantidad_toneladas: float
    precio_por_tonelada: Optional[float] = None
    fecha_inicio: date
    fecha_vencimiento: date
    activo: bool = Field(default=True)
```

## Modelos de Cereales y Calidad

### Cereal Base
```python
class Cereal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, max_length=50)  # "TRIGO", "MAIZ", "SOJA"
    codigo_senasa: str = Field(max_length=10)
    norma_calidad: str = Field(max_length=100)
    activo: bool = Field(default=True)

class AnalisisCalidad(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    operacion_id: int = Field(foreign_key="operacion.id")
    humedad_porcentaje: float
    peso_hectolitro: Optional[float] = None
    impurezas_porcentaje: float  
    granos_dañados_porcentaje: float
    proteina_porcentaje: Optional[float] = None
    grado_asignado: str = Field(max_length=20)  # "GRADO_1", "GRADO_2", etc.
    fecha_analisis: datetime = Field(default_factory=datetime.utcnow)
    analista_user_id: int = Field(foreign_key="user.id")
```

## Modelos de Operaciones y Estados

### Operación Principal
```python
class Operacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_operacion: str = Field(unique=True, max_length=50)
    camion_id: int = Field(foreign_key="camion.id")
    chofer_id: int = Field(foreign_key="chofer.id")
    empresa_id: int = Field(foreign_key="empresa.id")
    contrato_id: int = Field(foreign_key="contrato.id")
    cereal: str = Field(max_length=50)
    
    # Estados y timestamps
    estado_actual: str = Field(max_length=50)
    fecha_ingreso: Optional[datetime] = None
    fecha_egreso: Optional[datetime] = None
    
    # Pesos y mediciones
    peso_bruto_kg: Optional[float] = None
    peso_tara_kg: Optional[float] = None
    peso_neto_kg: Optional[float] = None
    
    # CPE relacionada
    numero_cpe: str = Field(max_length=50)
    cpe_validada: bool = Field(default=False)
    cpe_cerrada: bool = Field(default=False)
```

### Estados de Sectores
```python
class EstadoSector(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    operacion_id: int = Field(foreign_key="operacion.id")
    sector: str = Field(max_length=50)  # "PLAYA_CAMIONES", "CALADA", etc.
    estado: str = Field(max_length=50)
    timestamp_entrada: Optional[datetime] = None
    timestamp_salida: Optional[datetime] = None
    observaciones: Optional[str] = None
    usuario_registro_id: int = Field(foreign_key="user.id")
```

## Modelos de Cartas de Porte

### CPE Principal
```python
class CartaPorteElectronica(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_cpe: str = Field(unique=True, max_length=50)
    cuit_origen: str = Field(max_length=11)
    cuit_destino: str = Field(max_length=11)
    cuit_transportista: str = Field(max_length=11)
    
    # Datos de carga
    cereal: str = Field(max_length=50)
    peso_declarado_kg: float
    calidad_declarada: Optional[str] = Field(max_length=50)
    
    # Estados ARCA
    estado_arca: str = Field(max_length=20)  # "VIGENTE", "VENCIDA", "DESCARGADA"
    fecha_emision: datetime
    fecha_vencimiento: datetime
    
    # Validación
    validada_sistema: bool = Field(default=False)
    fecha_validacion: Optional[datetime] = None
    cerrada_sistema: bool = Field(default=False)
    fecha_cierre: Optional[datetime] = None
```

## Modelos de Respuestas ARCA

### Token ARCA
```python
class TokenArca(SQLModel):
    token: str
    sign: str  
    expiration: datetime
    service: str  # "CPE", "EMBARQUES", "FACTURACION"
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ConsultaCPEResponse(SQLModel):
    success: bool
    numero_cpe: str
    estado: str
    datos_mercaderia: Dict[str, Any] = {}
    datos_transporte: Dict[str, Any] = {}
    timestamp_consulta: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
```

## Relaciones Many-to-Many

### Patrón de Tabla Intermedia
```python
class User_Item_Relation(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    item_id: int = Field(foreign_key="item.id", primary_key=True)
    fecha_asignacion: datetime = Field(default_factory=datetime.utcnow)
    activo: bool = Field(default=True)

# En modelos principales usar back_populates
class User(SQLModel, table=True):
    items: List["Item"] = Relationship(back_populates="user", link_model=User_Item_Relation)

class Item(SQLModel, table=True):  
    users: List["User"] = Relationship(back_populates="item", link_model=User_Item_Relation)
```

## Validaciones y Constraints

### Validaciones Pydantic
```python
class OperacionCreate(SQLModel):
    numero_operacion: str = Field(min_length=5, max_length=50)
    peso_declarado_kg: float = Field(gt=0, le=60000)  # Máximo 60 toneladas
    
    @validator('numero_operacion')
    def validar_formato_operacion(cls, v):
        if not re.match(r'^OP\d{8}$', v):
            raise ValueError('Formato debe ser OPxxxxxxxx')
        return v
```

### Constraints de Base de Datos
```python
# Índices compuestos para performance
__table_args__ = (
    Index('idx_operacion_empresa_fecha', 'empresa_id', 'fecha_ingreso'),
    Index('idx_cpe_estado', 'numero_cpe', 'estado_arca'),
    UniqueConstraint('camion_id', 'fecha_ingreso', name='unique_camion_dia'),
)
```

## Configuración de Base de Datos

### Engine y Session
```python
from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "postgresql://user:pass@localhost/logigrain"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## Migración y Versionado

### Alembic Integration
```bash
# Generar migración
alembic revision --autogenerate -m "Agregar tabla analisis_calidad"

# Aplicar migraciones
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Uso en FastAPI

### Dependency Injection
```python
from fastapi import Depends
from sqlmodel import Session

@app.post("/operaciones/", response_model=Operacion)
def crear_operacion(
    operacion: OperacionCreate, 
    session: Session = Depends(get_session)
):
    db_operacion = Operacion.from_orm(operacion)
    session.add(db_operacion)
    session.commit()
    session.refresh(db_operacion)
    return db_operacion
```

## Reportes y Consultas

### Queries Típicas
```python
# Operaciones por empresa y período
def get_operaciones_empresa(session: Session, empresa_id: int, fecha_desde: date):
    return session.query(Operacion).filter(
        Operacion.empresa_id == empresa_id,
        Operacion.fecha_ingreso >= fecha_desde
    ).all()

# Análisis de calidad por cereal
def get_estadisticas_calidad(session: Session, cereal: str):
    return session.query(AnalisisCalidad).join(Operacion).filter(
        Operacion.cereal == cereal
    ).all()
```

## Contacto y Documentación

Para consultas sobre modelos de datos o esquemas:
- **Arquitecto de Datos**: data@logigrain.com
- **DBA Team**: dba@logigrain.com
- **Documentación SQLModel**: [https://sqlmodel.tiangolo.com/](https://sqlmodel.tiangolo.com/)
- **FastAPI Integration**: [https://fastapi.tiangolo.com/tutorial/sql-databases/](https://fastapi.tiangolo.com/tutorial/sql-databases/)