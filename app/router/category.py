from models.product_model import Category
from schemas.product_schema import CreateCategoryRequest, CategoryDataModel, CategoryDataModelList
from fastapi import HTTPException, Depends, APIRouter, Response
from database import SessionLocal
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from utils.security import get_current_active_admin
from utils.response_generator import ResponseGenerator
from fastapi import APIRouter
from utils.response_generator import ResponseModel, MessageResponse

router = APIRouter(
    prefix='/category',
    tags=['category']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/create-category/", status_code=201, dependencies=[Depends(get_current_active_admin)], response_model=ResponseModel[CategoryDataModel])
async def create_category(db: db_dependency, category: CreateCategoryRequest):
    """
    Endpoint to create a new category.

    Parameters:
    - category: The category data.

    Returns:
    - A dictionary with the created category data.

    Raises:
    - HTTPException with status code 500 if there is an error during database operations.
    """
    try:
        new_category = Category(name=category.name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return ResponseGenerator(new_category, Category.__name__).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-categories/", status_code=200, dependencies=[Depends(get_current_active_admin)], response_model=ResponseModel[CategoryDataModelList])
async def list_categories(db: db_dependency, page: int = 1, limit: int = 10):
    """
    Endpoint to list all categories.

    Parameters:
    - page: The page number.
    - limit: The number of items per page.

    Returns:
    - A dictionary with the list of categories.

    Raises:
    - HTTPException with status code 500 if there is an error during database operations.
    """
    categories = db.query(Category).offset((page - 1) * limit).limit(limit).all()
    return ResponseGenerator(categories, Category.__name__,).generate_response()

@router.get("/get-category/{category_id}/", status_code=200, dependencies=[Depends(get_current_active_admin)], response_model=ResponseModel[CategoryDataModel])
async def get_category(db: db_dependency, category_id: int):
    """
    Endpoint to get a category by ID.

    Parameters:
    - category_id: The category ID.

    Returns:
    - A dictionary with the category data.

    Raises:
    - HTTPException with status code 404 if the category does not exist.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    return ResponseGenerator(category, Category.__name__,).generate_response()

@router.put("/update-category", status_code=200, dependencies=[Depends(get_current_active_admin)], response_model=ResponseModel[CategoryDataModel])
async def update_category(db: db_dependency, category: CreateCategoryRequest):
    """
    Update a category in the database.

    Args:
        category (CreateCategoryRequest): The category data to update.

    Returns:
        dict: The updated category data.

    Raises:
        HTTPException: If the category is not found or if there is a database error.
    """
    existing_category = db.query(Category).filter(Category.id == category.id).first()
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found.")
    try:
        existing_category.name = category.name
        db.commit()
        db.refresh(existing_category)
        return ResponseGenerator(existing_category, Category.__name__,).generate_response()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/delete-category/{category_id}/", status_code=200, dependencies=[Depends(get_current_active_admin)], response_model=MessageResponse)
async def delete_category(db: db_dependency, category_id: int):
    """
    Delete a category from the database.

    Args:
        category_id (int): The ID of the category to delete.

    Returns:
        dict: A dictionary containing a success message if the category is deleted successfully.

    Raises:
        HTTPException: If the category is not found or if there is an error during deletion.
    """
    existing_category = db.query(Category).filter(Category.id == category_id).first()
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found.")
    try:
        db.delete(existing_category)
        db.commit()
        return {"message": "Category deleted successfully."}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))