from pydantic import BaseModel
from datetime import date, datetime
from typing import List
from typing import Optional

class CreateProductDealRequest(BaseModel):
    id: Optional[int]
    title: str
    price: Optional[int]
    total_rating: Optional[int]
    img: Optional[str]
    discount: Optional[int]
    url: Optional[str]
    date: Optional[date]
    category_id: int

class CreateCategoryRequest(BaseModel):
    id: Optional[int]
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str
    updated_at: datetime
    create_at: datetime

class CategoryDataModel(BaseModel):
    Category: CategoryResponse

class CategoryDataModelList(BaseModel):
    Category: List[CategoryResponse]