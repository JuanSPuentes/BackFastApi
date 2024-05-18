from fastapi import FastAPI, status, Depends, HTTPException
from models import UserModel, ProductModel
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from router.auth import get_current_user, router as auth_router
from router.product import router as product_router
from utils.security import get_current_active_user

app = FastAPI()
app.include_router(auth_router)
app.include_router(product_router)

UserModel.Base.metadata.create_all(bind=engine)
ProductModel.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get('/', status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_user)])
async def user(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication empty')
    return {'user': user}
