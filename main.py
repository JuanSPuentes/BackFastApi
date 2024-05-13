from fastapi import FastAPI, status, Depends, HTTPException
import models
import auth
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from auth import get_current_user

app = FastAPI()
app.include_router(auth.router)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

def get_current_active_admin(current_user: user_dependency):
    if current_user['user_type'] != models.UserType.admin.value:
        raise HTTPException(status_code=400, detail="Not an admin")
    return current_user

@app.get('/', status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_admin)])
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication empty')
    return {'user': user}
