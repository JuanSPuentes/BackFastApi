from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from models.user_model import  UserType
from typing import Annotated

SECRET_KEY = 'ASqJt}rMH[Qp.0rFlri0;@P1P*Ve1$e+qD3A<$"`pQ)AB:.@&t}w-zBdWuw*n`|'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

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
    
user_dependency = Annotated[dict, Depends(get_current_user)]

def get_current_active_admin(current_user: user_dependency):
    if current_user['user_type'] != UserType.admin.value:
        raise HTTPException(status_code=403, detail="Not an admin")
    return current_user

def get_current_active_user(current_user: user_dependency):
    if current_user['user_type'] != UserType.user.value or current_user['user_type'] != UserType.admin.value:
        return current_user
    raise HTTPException(status_code=403, detail="Not an user")
    