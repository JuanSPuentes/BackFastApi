from database import Base
from sqlalchemy import Column, Integer, String
from enum import Enum

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    user_type = Column(String)

class UserType(str, Enum):
    admin = "admin"
    user = "user"
    mod = "mod"
