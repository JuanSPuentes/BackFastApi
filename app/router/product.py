from fastapi import UploadFile, File, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import insert
import pandas as pd
from database import SessionLocal
from router.auth import get_current_user
from utils.security import get_current_active_user, get_current_active_admin
from models.product_model import ProductDeal, DataLoadLog
from datetime import datetime, date

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

@router.post("/load-products/", status_code=201, dependencies=[Depends(get_current_active_admin)])
async def create_upload_file(db: db_dependency, file: UploadFile = File(...)):
    """
    Endpoint to upload a CSV file and insert its data into the database.

    Parameters:
    - db: The database dependency.
    - file: The uploaded file in CSV format.

    Returns:
    - A dictionary with a success message if the file was processed and data inserted successfully.

    Raises:
    - HTTPException with status code 500 if there is an error during database operations.
    - HTTPException with status code 400 if the file is not in CSV format.
    """
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
        raise HTTPException(
            status_code=400, detail="File must be in CSV format.")

@router.get("/list-products/", status_code=200, dependencies=[Depends(get_current_active_user)])
async def list_products(db: db_dependency, page: int = 1, limit: int = 10):
    """
    Retrieve a list of products.

    Args:
        page (int, optional): The page number. Defaults to 1.
        limit (int, optional): The number of items per page. Defaults to 10.

    Returns:
        dict: A dictionary containing the list of products and pagination information.
    """
    try:
        query = db.query(ProductDeal).filter(ProductDeal.active == 1).offset(
            (page - 1) * limit).limit(limit).all()
        return {"data": query,
                'pagination':
                {'current_page': page, 'limit_per_page': limit, 'item_per_page': len(query), 'next_page': page + 1 if len(query) == limit else None, 'previous_page': page - 1 if page > 1 else None, 'total_items': db.query(ProductDeal).filter(ProductDeal.active == 1).count()}}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/products/deactivate-all-by-date/", status_code=200, dependencies=[Depends(get_current_active_admin)])
async def deactivate_all_products(db: db_dependency, date: date = datetime.now().date()):
    """
    Deactivates all products for a given date.
    
    Args:
        date (date, optional): The date to deactivate products for. Defaults to the current date.
    
    Returns:
        dict: A dictionary containing a success message.
    
    Raises:
        HTTPException: If there is an error during the deactivation process.
    """
    try:
        db.query(ProductDeal).where(ProductDeal.date == date).update({ProductDeal.active: 0})
        db.commit()
        return {"message": "All products deactivated successfully."}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

""" /products/delete-product-by-id/ """
""" /products/delete-product-by-date/ """
""" /products/create-product/ """
""" /products/get-product-by-id/ """
""" /products/get-product-by-category/ """