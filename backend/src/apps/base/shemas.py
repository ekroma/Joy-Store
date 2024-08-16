from pydantic import BaseModel
from typing import TypeVar, Generic

T = TypeVar("T")

class MessageResponse(BaseModel):
    message:str

class SuccessResponse(BaseModel):
    detail:str = "1000"

class PaginationBase(BaseModel, Generic[T]):
    page: int
    page_size: int
    total: int
    items:list[T]
    
    class Config:
        from_attributes = True

class LanguageScheme(BaseModel):
    language_code:str
    name:str