from sqlalchemy import create_engine, String, Float, Integer, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import os
from flask_login import UserMixin

import bcrypt # pip install bcrypt

DATABASE_URL = os.environ.get("DATABASE_URL")

# Fallback для локального запуску (опціонально)
if not DATABASE_URL:
    PGUSER = "postgres"
    PGPASSWORD = "21022004"
    DATABASE_URL = f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@localhost:5432/restaurant_illia"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
# Базовий клас для моделей
class Base(DeclarativeBase):
    def create_db(self):
        Base.metadata.create_all(engine)

    def drop_db(self):
        Base.metadata.drop_all(engine)

class Users(Base, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    nickname : Mapped[str] = mapped_column(String(100), unique=True)
    password : Mapped[str] = mapped_column(String(200))
    email : Mapped[str] = mapped_column(String(50), unique=True)

    reservations = relationship("Reservation", foreign_keys="Reservation.user_id" ,back_populates="user")
    orders = relationship("Orders", foreign_keys="Orders.user_id", back_populates='user')

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Menu(Base):
    __tablename__ = "menu"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    weight: Mapped[str] = mapped_column(String)
    ingredients : Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column()
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    file_name: Mapped[str] = mapped_column(String)

class Reservation(Base):
    __tablename__ = "reservation"
    id: Mapped[int] = mapped_column(primary_key=True)
    time_start: Mapped[datetime] = mapped_column(DateTime)
    type_table: Mapped[str] = mapped_column(String(20))
    user_id : Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship("Users", foreign_keys="Reservation.user_id" ,back_populates="reservations")

class Orders(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_list: Mapped[dict] = mapped_column(JSONB)
    order_time: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship("Users", foreign_keys="Orders.user_id", back_populates="orders")

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