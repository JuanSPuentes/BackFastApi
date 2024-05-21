from typing import Any, Dict, Generic, Optional, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")
class ResponseModel(BaseModel, Generic[T]):
    data: T 
    additional_data: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    message: str
    
class ResponseGenerator:
    def __init__(self, data, obj = str, additional_data=None):
        self.data = data
        self.additional_data = additional_data
        self.obj = obj
    
    def generate_response(self):
        return {"data": { self.obj : self.data} , "additional_data": self.additional_data}