from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre_completo: str
    username: str
    password: str
    email: str

class Item(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    habilitado: bool = True
    
    
class User_Item_Relation(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    item_id: int = Field(foreign_key="item.id", primary_key=True)

    user: Optional[User] = Relationship(back_populates="items")
    item: Optional[Item] = Relationship(back_populates="users")
    
User.items = Relationship(back_populates="user", link_model=User_Item_Relation)
Item.users = Relationship(back_populates="item", link_model=User_Item_Relation) 

