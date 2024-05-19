from fastapi import UploadFile, File, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import insert
import pandas as pd
from database import SessionLocal
from utils.security import get_current_active_user, get_current_active_admin
from models.product_model import ProductDeal, DataLoadLog, Category
from datetime import datetime, date
from utils.response_generator import ResponseGenerator

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

@router.post("/load-products-by-category/", status_code=201, dependencies=[Depends(get_current_active_admin)])
async def load_products_by_category(db: db_dependency, category_id: int, file: UploadFile = File(...)):
    """
    Endpoint to upload a CSV file and insert its data into the database.

    Parameters:
    - file: The uploaded file in CSV format.
    - category_id: The category ID for the products.

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
            category_id = db.query(Category).filter(Category.id == category_id).first()
            if not category_id:
                raise HTTPException(status_code=404, detail="Category not found.")
            df['category_id'] = category_id.id
            items = df.to_dict(orient='records')
            stmt = insert(ProductDeal)
            db.execute(stmt, items)
            db.commit()
            return {"message": f"File successfully processed and a total of {df.count().iloc[0]} data inserted into the database."}
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
        query = db.query(ProductDeal).filter(ProductDeal.active == 1).where(ProductDeal.deleted == 0).offset(
            (page - 1) * limit).limit(limit).all()
        additional_data = {'current_page': page, 'limit_per_page': limit, 'item_per_page': len(query), 'next_page': page + 1 if len(query) == limit else None, 'previous_page': page - 1 if page > 1 else None, 'total_items': db.query(ProductDeal).filter(ProductDeal.active == 1).filter(ProductDeal.deleted == 0).count()}
        return ResponseGenerator(query, ProductDeal.__name__ , additional_data).generate_response()
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

@router.put("/delete-product-by-id/", status_code=200, dependencies=[Depends(get_current_active_admin)])
async def delete_product_by_id(db: db_dependency, product_id: int):
    """
    Delete a product by its ID.

    Args:
        product_id (int): The ID of the product to be deleted.

    Returns:
        dict: A dictionary representing the deleted product.

    Raises:
        HTTPException: If there is an error during the deletion process.
    """
    try:
        db.query(ProductDeal).where(ProductDeal.id == product_id).update({ProductDeal.deleted: 1})
        product = db.query(ProductDeal).filter(ProductDeal.id == product_id).first()
        db.commit()
        return ResponseGenerator(product.as_dict(), ProductDeal.__name__).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/delete-product-by-date/", status_code=200, dependencies=[Depends(get_current_active_admin)])
async def delete_product_by_date(db: db_dependency, date: date = datetime.now().date()):
    """
    Delete products by date.

    Args:
        db (db_dependency): The database dependency.
        date (date, optional): The date to filter the products. Defaults to the current date.

    Returns:
        dict: A dictionary containing the message indicating the number of products deleted.

    Raises:
        HTTPException: If there are no products found for the given date or if there is a database error.
    """
    try:
        product_list = db.query(ProductDeal).filter(ProductDeal.date == date).filter(ProductDeal.deleted == 0)
        total_products = product_list.count()
        if total_products == 0:
            raise HTTPException(status_code=404, detail="No products found for the given date.")
        product_list.update({ProductDeal.deleted: 1})
        db.commit()
        return {"message": f"Total {total_products} Products deleted successfully"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

""" /products/create-product/ """
""" /products/get-product-by-id/ """
""" /products/get-product-by-category/ """
""" /products/order-product-by-discount/ """