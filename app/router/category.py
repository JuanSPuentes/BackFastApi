from models.product_model import Category, CreateCategoryRequest
from fastapi import HTTPException, Depends, APIRouter
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from utils.security import get_current_active_admin
from utils.response_generator import ResponseGenerator

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

@router.post("/create-category/", status_code=201, dependencies=[Depends(get_current_active_admin)])
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
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return ResponseGenerator(new_category, Category.__name__,).generate_response()

@router.get("/list-categories/", status_code=200, dependencies=[Depends(get_current_active_admin)])
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