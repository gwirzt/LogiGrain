"""
Script para inicializar datos de prueba en LogiGrain.
Crea usuarios, puertos y relaciones para testing del sistema de login.
"""

from sqlmodel import SQLModel, create_engine, Session
from Modelos.usuario import Usuario, Puerto, UsuarioPuerto
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración de base de datos
DATABASE_URL = "sqlite:///./logigrain.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_database():
    """Inicializar base de datos con datos de prueba"""
    
    # Crear tablas
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        print("🏗️ Inicializando base de datos LogiGrain...")
        
        # === CREAR PUERTOS === #
        print("\n📍 Creando puertos...")
        
        puertos_data = [
            {
                "nombre": "Terminal Rosario Puerto 1",
                "codigo": "TRP1",
                "descripcion": "Terminal principal de cereales - Rosario",
                "ubicacion": "Puerto de Rosario - Zona Norte"
            },
            {
                "nombre": "Terminal Rosario Puerto 2", 
                "codigo": "TRP2",
                "descripcion": "Terminal secundario - Soja y Trigo",
                "ubicacion": "Puerto de Rosario - Zona Sur"
            },
            {
                "nombre": "Terminal San Lorenzo",
                "codigo": "TSL1",
                "descripcion": "Terminal de exportación San Lorenzo",
                "ubicacion": "Puerto San Lorenzo"
            }
        ]
        
        puertos_creados = []
        for puerto_info in puertos_data:
            # Verificar si el puerto ya existe
            puerto_existente = session.query(Puerto).filter(Puerto.codigo == puerto_info["codigo"]).first()
            if not puerto_existente:
                puerto = Puerto(**puerto_info)
                session.add(puerto)
                puertos_creados.append(puerto)
                print(f"  ✅ Puerto creado: {puerto_info['codigo']} - {puerto_info['nombre']}")
            else:
                puertos_creados.append(puerto_existente)
                print(f"  ℹ️ Puerto existente: {puerto_info['codigo']}")
        
        session.commit()
        
        # === CREAR USUARIOS === #
        print("\n👥 Creando usuarios...")
        
        usuarios_data = [
            {
                "username": "admin",
                "password": "admin123",
                "nombre_completo": "Administrador del Sistema",
                "email": "admin@logigrain.com",
                "es_admin": True
            },
            {
                "username": "operador1",
                "password": "op123",
                "nombre_completo": "Juan Carlos Operador",
                "email": "operador1@logigrain.com",
                "es_admin": False
            },
            {
                "username": "supervisor",
                "password": "super123",
                "nombre_completo": "María Elena Supervisora",
                "email": "supervisor@logigrain.com", 
                "es_admin": False
            },
            {
                "username": "gerente",
                "password": "ger123",
                "nombre_completo": "Roberto Martín Gerente",
                "email": "gerente@logigrain.com",
                "es_admin": False
            }
        ]
        
        usuarios_creados = []
        for user_info in usuarios_data:
            # Verificar si el usuario ya existe
            usuario_existente = session.query(Usuario).filter(Usuario.username == user_info["username"]).first()
            if not usuario_existente:
                usuario = Usuario(
                    username=user_info["username"],
                    nombre_completo=user_info["nombre_completo"],
                    email=user_info["email"],
                    es_admin=user_info["es_admin"]
                )
                usuario.set_password(user_info["password"])
                session.add(usuario)
                usuarios_creados.append(usuario)
                print(f"  ✅ Usuario creado: {user_info['username']} - {user_info['nombre_completo']}")
            else:
                usuarios_creados.append(usuario_existente)
                print(f"  ℹ️ Usuario existente: {user_info['username']}")
        
        session.commit()
        
        # === ASIGNAR USUARIOS A PUERTOS === #
        print("\n🔗 Asignando usuarios a puertos...")
        
        # Admin tiene acceso a todos los puertos
        admin = next(u for u in usuarios_creados if u.username == "admin")
        for puerto in puertos_creados:
            relacion_existente = session.query(UsuarioPuerto).filter(
                UsuarioPuerto.usuario_id == admin.id,
                UsuarioPuerto.puerto_id == puerto.id
            ).first()
            
            if not relacion_existente:
                relacion = UsuarioPuerto(usuario_id=admin.id, puerto_id=puerto.id)
                session.add(relacion)
                print(f"  ✅ Admin asignado a: {puerto.codigo}")
        
        # Operador1 solo a TRP1 y TRP2
        operador1 = next(u for u in usuarios_creados if u.username == "operador1")
        puertos_operador = [p for p in puertos_creados if p.codigo in ["TRP1", "TRP2"]]
        for puerto in puertos_operador:
            relacion_existente = session.query(UsuarioPuerto).filter(
                UsuarioPuerto.usuario_id == operador1.id,
                UsuarioPuerto.puerto_id == puerto.id
            ).first()
            
            if not relacion_existente:
                relacion = UsuarioPuerto(usuario_id=operador1.id, puerto_id=puerto.id)
                session.add(relacion)
                print(f"  ✅ Operador1 asignado a: {puerto.codigo}")
        
        # Supervisor a TRP2 y TSL1
        supervisor = next(u for u in usuarios_creados if u.username == "supervisor")
        puertos_supervisor = [p for p in puertos_creados if p.codigo in ["TRP2", "TSL1"]]
        for puerto in puertos_supervisor:
            relacion_existente = session.query(UsuarioPuerto).filter(
                UsuarioPuerto.usuario_id == supervisor.id,
                UsuarioPuerto.puerto_id == puerto.id
            ).first()
            
            if not relacion_existente:
                relacion = UsuarioPuerto(usuario_id=supervisor.id, puerto_id=puerto.id)
                session.add(relacion)
                print(f"  ✅ Supervisor asignado a: {puerto.codigo}")
        
        # Gerente solo a TSL1
        gerente = next(u for u in usuarios_creados if u.username == "gerente")
        puerto_gerente = next(p for p in puertos_creados if p.codigo == "TSL1")
        relacion_existente = session.query(UsuarioPuerto).filter(
            UsuarioPuerto.usuario_id == gerente.id,
            UsuarioPuerto.puerto_id == puerto_gerente.id
        ).first()
        
        if not relacion_existente:
            relacion = UsuarioPuerto(usuario_id=gerente.id, puerto_id=puerto_gerente.id)
            session.add(relacion)
            print(f"  ✅ Gerente asignado a: {puerto_gerente.codigo}")
        
        session.commit()
        
        print("\n🎉 ¡Base de datos inicializada correctamente!")
        print("\n📋 USUARIOS DE PRUEBA:")
        print("  👤 admin / admin123 - Acceso a todos los puertos (Admin)")
        print("  👤 operador1 / op123 - Acceso a TRP1, TRP2")
        print("  👤 supervisor / super123 - Acceso a TRP2, TSL1") 
        print("  👤 gerente / ger123 - Acceso a TSL1")
        print("\n🔑 Usar estos credenciales para probar el endpoint /login")

if __name__ == "__main__":
    init_database()