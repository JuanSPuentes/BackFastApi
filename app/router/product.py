from fastapi import UploadFile, File, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import insert
import pandas as pd
from database import SessionLocal
from router.auth import get_current_user
from utils.security import get_current_active_user, get_current_active_admin
from models.ProductModel import ProductDeal, DataLoadLog

router = APIRouter(
    prefix='/product',
    tags=['product'] 
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/uploadfile/", status_code=201, dependencies=[Depends(get_current_active_admin)])
async def create_upload_file(db: db_dependency, file: UploadFile = File(...)):
    if file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file.file)
            df['date'] = pd.to_datetime(df['date'])
            items = df.to_dict(orient='records')
            stmt = insert(ProductDeal)
            db.execute(stmt, items)
            db.commit()
            return {"message": "File successfully processed and data inserted into database."}
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="File must be in CSV format.")
        