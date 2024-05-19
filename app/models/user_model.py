from database import Base
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import Column, Integer, String
from enum import Enum

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    user_type = Column(String)

class CreateUserRequest(BaseModel):
    username: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return password

class UserType(str, Enum):
    admin = "admin"
    user = "user"
    mod = "mod"
