from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from .user import ReturnUser

class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool = True
    created_at: datetime
    owner_id: int
    owner: ReturnUser
    
    class Config:
        orm_mode = True


class CreatePost(BaseModel):
    title: str
    content: str
    published: bool = True


class SearchPost(BaseModel):
    id: int


class UpdatePost(BaseModel):
    id: int
    title: Optional[str]
    content: Optional[str]
    published: Optional[bool] = True