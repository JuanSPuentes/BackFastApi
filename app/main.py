from fastapi import FastAPI, status, Depends, HTTPException
from models import user_model, product_model
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from router.auth import get_current_user, router as auth_router
from router.product import router as product_router
from router.category  import router as category_router
from utils.security import get_current_active_user
from utils.response_generator import ResponseGenerator
from fastapi.openapi.utils import get_openapi
from utils.response_generator import ResponseModel
from schemas.auth_schema import UserDataModel, UserResponse

app = FastAPI()
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(category_router)

user_model.Base.metadata.create_all(bind=engine)
product_model.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI Custom OpenAPI",
        version="1.0.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

@app.get('/', status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_user)], response_model=ResponseModel[UserDataModel])
async def user(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication empty')
    return ResponseGenerator(user, user_model.User.__name__,).generate_response()
