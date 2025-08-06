from sqlalchemy import create_engine, String, Float, Integer, ForeignKey, Boolean, Text, DateTime, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    PGUSER = "postgres"
    PGPASSWORD = "ilya2012"
    DATABASE_URL = f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@localhost:5432/proekt_db"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    def create_db(self):
        Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)

class Menu(Base):
    __tablename__ = "menu"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    ingredients: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column()
    weight: Mapped[int] = mapped_column()
    image_url: Mapped[str] = mapped_column(String(255))

class Orders(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
    user = relationship("User")
    item = relationship("Menu")

class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    time: Mapped[str] = mapped_column(String(50))
    user = relationship("User")

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

base = Base()
base.create_db()








#####################################################################################


# engine = create_engine(DATABASE_URL, echo=True)
# Session = sessionmaker(bind=engine)

# class Base(DeclarativeBase):
#     pass

# class User(Base):
#     __tablename__ = "users"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     username: Mapped[str] = mapped_column(String(50), unique=True)
#     password: Mapped[str] = mapped_column(String(50))
#     email: Mapped[str] = mapped_column(String(100), unique=True)

# class Menu(Base):
#     __tablename__ = "menu"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(100))
#     description: Mapped[str] = mapped_column(String(255))
#     ingredients: Mapped[str] = mapped_column(String(255))
#     price: Mapped[float] = mapped_column()
#     weight: Mapped[int] = mapped_column()
#     image_url: Mapped[str] = mapped_column(String(255))

# class Order(Base):
#     __tablename__ = "orders"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     item_id: Mapped[int] = mapped_column(ForeignKey("menu.id"))
#     user = relationship("User")
#     item = relationship("Menu")

# class Reservation(Base):
#     __tablename__ = "reservations"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     time: Mapped[str] = mapped_column(String(50))
#     user = relationship("User")

# Base.metadata.create_all(engine)