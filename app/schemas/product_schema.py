from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List
from typing import Optional

class CreateProductDealRequest(BaseModel):
    id: Optional[int] = None
    title: str = None
    price: Optional[float] = None
    total_rating: Optional[int] = None
    img: Optional[str] = None
    discount: Optional[int] = None
    url: Optional[str] = None
    date: Optional[date]
    category_id: int = None

class CreateCategoryRequest(BaseModel):
    id: Optional[int]
    name: str

class ProductDealResponse(BaseModel):
    id: int
    title: str
    price: float
    total_rating: int
    img: str
    discount: int
    url: str
    date: date
    active: int
    deleted: int
    category_id: int
    updated_at: datetime
    create_at: datetime

class CategoryResponse(BaseModel):
    id: int
    name: str
    updated_at: datetime
    create_at: datetime

class ProductDealDataModel(BaseModel):
    ProductDeal: ProductDealResponse

class ProductDealDataModelList(BaseModel):
    ProductDeal: List[ProductDealResponse]

class CategoryDataModel(BaseModel):
    Category: CategoryResponse

class CategoryDataModelList(BaseModel):
    Category: List[CategoryResponse]