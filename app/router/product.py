from fastapi import UploadFile, File, HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import insert
import pandas as pd
from database import SessionLocal
from utils.security import get_current_active_user, get_current_active_admin
from models.product_model import ProductDeal, Category
from schemas.product_schema import CreateProductDealRequest
from datetime import datetime, date
from utils.response_generator import ResponseGenerator, MessageResponse, ResponseModel
from schemas.product_schema import ProductDealDataModelList, ProductDealDataModel

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

@router.post("/load-products-by-category/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_admin)], response_model=MessageResponse)
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
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
            df['category_id'] = category_id.id
            df['price'] = df['price'].str.replace('$', '').astype(str).str.replace(',', '').astype(float)
            df['discount'] = df['discount'].str.replace('%', '').str.replace('-', '').astype(str).str.replace(',', '').astype(int)
            df['total_rating'] = df['total_rating'].str.replace(',', '').astype(int)
            items = df.to_dict(orient='records')
            stmt = insert(ProductDeal)
            db.execute(stmt, items)
            db.commit()
            return {"message": f"File successfully processed and a total of {df.count().iloc[0]} data inserted into the database."}
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be in CSV format.")

@router.get("/list-products/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_user)], response_model=ResponseModel[ProductDealDataModelList])
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put("/products/deactivate-all-by-date/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_admin)], response_model=MessageResponse)
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
        products = db.query(ProductDeal).filter(ProductDeal.date == date)
        total_products = products.count()
        products.update({ProductDeal.active: 0})
        db.commit()
        return {"message": "Total {} Products deactivated successfully".format(total_products)}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/delete-product-by-id/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_admin)], response_model=ResponseModel[ProductDealDataModel])
async def delete_product_by_id(db: db_dependency, product_id: int):
    """
    Delete a product by its ID.

    Args:
        product_id (int): The ID of the product to delete.

    Returns:
        ResponseModel[ProductDealDataModel]: The response model containing the deleted product data.

    Raises:
        HTTPException: If the product is not found or has already been deleted.
        HTTPException: If there is an error with the database operation.
    """
    try:
        product = db.query(ProductDeal).filter(ProductDeal.id == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        elif product.deleted == 1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product already deleted.")
        db.query(ProductDeal).where(ProductDeal.id == product_id).update({ProductDeal.deleted: 1})
        db.commit()
        return ResponseGenerator(product.as_dict(), ProductDeal.__name__).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put("/delete-product-by-date/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_admin)], response_model=MessageResponse)
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found for the given date.")
        product_list.update({ProductDeal.deleted: 1})
        db.commit()
        return {"message": f"Total {total_products} Products deleted successfully"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/create-product/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_admin)], response_model=ResponseModel[ProductDealDataModel])
async def create_product(db: db_dependency, product: CreateProductDealRequest):
    """
    Create a product.

    Args:
        product (ProductDeal): The product data to be created.

    Returns:
        dict: A dictionary representing the created product.

    Raises:
        HTTPException: If there is an error during the creation process.
    """
    try:
        category_id = db.query(Category).filter(Category.id == product.category_id).first()
        if not category_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        new_product = ProductDeal(**product.model_dump(exclude={'id'}))
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return ResponseGenerator(new_product, ProductDeal.__name__).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/get-product-by-id/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_user)], response_model=ResponseModel[ProductDealDataModel])
async def get_product_by_id(db: db_dependency, product_id: int):
    """
    Retrieve a product by its ID.

    Args:
        product_id (int): The ID of the product to retrieve.

    Returns:
        dict: The response containing the product details.

    Raises:
        HTTPException: If the product is not found or there is a server error.
    """
    try:
        product = db.query(ProductDeal).filter(ProductDeal.id == product_id).filter(ProductDeal.active == 1).filter(ProductDeal.deleted == 0).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        return ResponseGenerator(product, ProductDeal.__name__).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/get-product-by-category/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_user)], response_model=ResponseModel[ProductDealDataModelList])
async def get_product_by_category(db: db_dependency, category_id: int, page: int = 1, limit: int = 10):
    """
    Get products by category.

    Args:
        category_id (int): The category ID to filter the products.
        page (int, optional): The page number. Defaults to 1.
        limit (int, optional): The number of items per page. Defaults to 10.

    Returns:
        dict: A dictionary containing the list of products and pagination information.

    Raises:
        HTTPException: If there is an error during the retrieval process.
    """
    try:
        query = db.query(ProductDeal).filter(ProductDeal.category_id == category_id).filter(ProductDeal.active == 1).filter(ProductDeal.deleted == 0).offset(
            (page - 1) * limit).limit(limit).all()
        additional_data = {'current_page': page, 'limit_per_page': limit, 'item_per_page': len(query), 'next_page': page + 1 if len(query) == limit else None, 'previous_page': page - 1 if page > 1 else None, 'total_items': db.query(ProductDeal).filter(ProductDeal.category_id == category_id).filter(ProductDeal.active == 1).filter(ProductDeal.deleted == 0).count()}
        return ResponseGenerator(query, ProductDeal.__name__ , additional_data).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/get-product-by-discount/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_user)], response_model=ResponseModel[ProductDealDataModelList])
async def get_product_by_discount(db: db_dependency, page: int = 1, limit: int = 10, order: str = "desc"):
    """
    Get products by discount.

    Args:
        page (int, optional): The page number. Defaults to 1.
        limit (int, optional): The number of items per page. Defaults to 10.
        order (str, optional): The order of the results. Must be 'asc' or 'desc'. Defaults to 'desc'.

    Returns:
        dict: The response containing the queried products, additional data, and status code.

    Raises:
        HTTPException: If the order parameter is not 'asc' or 'desc'.
        HTTPException: If there is an error executing the database query.
    """
    try:    
        if order not in ["asc", "desc"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must be 'asc' or 'desc'")
        order_criteria = ProductDeal.discount.asc() if order == "asc" else ProductDeal.discount.desc()
        query = db.query(ProductDeal).filter(ProductDeal.active == 1).filter(ProductDeal.deleted == 0).order_by(order_criteria).offset(
            (page - 1) * limit).limit(limit).all()
        additional_data = {'current_page': page, 'limit_per_page': limit, 'item_per_page': len(query), 'next_page': page + 1 if len(query) == limit else None, 'previous_page': page - 1 if page > 1 else None, 'total_items': db.query(ProductDeal).filter(ProductDeal.discount > 0).filter(ProductDeal.active == 1).filter(ProductDeal.deleted == 0).count()}
        return ResponseGenerator(query, ProductDeal.__name__ , additional_data).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put("/update-product/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_admin)], response_model=ResponseModel[ProductDealDataModel])
async def update_product(db: db_dependency, product: CreateProductDealRequest):
    """
    Update a product.

    Args:
        product (CreateProductDealRequest): The product data to update.

    Returns:
        dict: The updated product data.

    Raises:
        HTTPException: If the product is not found or if there is a database error.
    """
    try:
        product_data = db.query(ProductDeal).filter(ProductDeal.id == product.id).filter(ProductDeal.active == 1).filter(ProductDeal.deleted == 0).first()
        if not product_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        if product.category_id:
            category_id = db.query(Category).filter(Category.id == product.category_id).first()
        else:
            category_id = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        update_data = product.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product_data, key, value)
        db.commit()
        db.refresh(product_data)
        return ResponseGenerator(product_data, ProductDeal.__name__).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
