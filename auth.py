from datetime import timedelta, datetime, UTC
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status 
from database import SessionLocal
from models import User, UserType
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import Optional
from models import UserType

router = APIRouter(
    prefix='/auth',
    tags=['auth'] 
)

SECRET_KEY = 'ASqJt}rMH[Qp.0rFlri0;@P1P*Ve1$e+qD3A<$"`pQ)AB:.@&t}w-zBdWuw*n`|'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_type: Optional[UserType] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_type: UserType = payload.get("user_type")
        if username is None or user_id is None:
            raise credentials_exception
        return {'username': username, 'user_id': user_id, 'user_type': user_type}
    except JWTError:
        raise credentials_exception
    
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequest, db: db_dependency):
    create_user_model = User(username=request.username, hashed_password=bcrypt_context.hash(request.password))
    db.add(create_user_model)
    db.commit()

@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    token = create_access_token(username = user.username, user_id = user.id, user_type = user.user_type, expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {'access_token': token, 'token_type': 'bearer'}

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return user

def create_access_token(username: str, user_id: int, user_type: str, expires_delta: timedelta):
    to_encode = {'exp': datetime.now(UTC) + expires_delta, 'sub': username, 'id': user_id, 'user_type': user_type}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_active_admin(current_user: user_dependency):
    if current_user['user_type'] != UserType.admin.value:
        raise HTTPException(status_code=400, detail="Not an admin")
    return current_user

def get_current_active_user(current_user: user_dependency):
    if current_user['user_type'] != UserType.user.value:
        raise HTTPException(status_code=400, detail="Not an user")
    return current_user