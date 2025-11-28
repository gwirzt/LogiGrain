# models.py
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str

class Item(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    owner_id: int
