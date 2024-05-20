from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, HttpUrl
from typing import Optional
from sqlalchemy import Column, Integer, Date, String, ForeignKey, Numeric, DateTime
from datetime import date

class DataLoadLog(Base):
    __tablename__ = "data_load_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=func.current_date())
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    create_at = Column(DateTime, default=func.current_timestamp())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class ProductDeal(Base):
    __tablename__ = "product_deals"

    id = Column(Integer, primary_key=True, index=True)
    title =  Column(String)
    price = Column(String, nullable=True)
    total_rating = Column(Integer, nullable=True)
    img = Column(String)
    discount = Column(Integer, nullable=True)
    url = Column(String)
    date = Column(Date, default=func.current_timestamp())
    active = Column(Integer, default=1)
    deleted = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", backref="product_deals")
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    create_at = Column(DateTime, default=func.current_timestamp())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class CreateDataLoadLogRequest(BaseModel):
    date:Optional[date]

class CreateProductDealRequest(BaseModel):
    id: Optional[int]
    title: str
    price: Optional[int]
    total_rating: Optional[int]
    img: HttpUrl
    discount: Optional[int]
    url: HttpUrl

class CreateCategoryRequest(BaseModel):
    id: Optional[int]
    name: str