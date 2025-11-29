# main.py
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, create_engine, SQLModel, Field
from typing import List
from Modelos.usuario import User, Item,User_Item_Relation

# Configuración de la base de datos

DATABASE_URL = "sqlite:///database.db"  # Cambia esto según tu base de datos

engine = create_engine(DATABASE_URL)

# Crear la aplicación FastAPI
app = FastAPI()

# Crear la base de datos
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Rutas
@app.post("/users/", response_model=User)
def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@app.get("/users/", response_model=List[User])
def read_users():
    with Session(engine) as session:
        users = session.exec(User.select()).all()
        return users
