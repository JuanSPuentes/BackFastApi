from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from models.user_model import UserType

class CreateUserRequest(BaseModel):
    username: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return password

class UserResponse(BaseModel):
    username: EmailStr
    user_type: UserType
    
class UserDataModel(BaseModel):
    User: UserResponse

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_type: Optional[UserType] = None
