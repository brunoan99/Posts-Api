from datetime import datetime
from pydantic import BaseModel

from ..schemas.post import Post
from ..schemas.user import ReturnUserComment


class Comment(BaseModel):
    id: int
    content: str
    created_at: datetime
    post_id: int
    post: Post
    
    owner_id: int
    owner: ReturnUserComment
    
    class Config:
        orm_mode = True


class CommentFromPost(BaseModel):
    id: int
    content: str
    created_at: datetime
    post_id: int
    owner_id: int
    
    owner: ReturnUserComment
    
    class Config:
        orm_mode = True


class CommentFromUser(BaseModel):
    id: int
    content: str
    created_at: datetime
    post_id: int
    post: Post
    
    owner_id: int

    class Config:
        orm_mode = True


class CreateComment(BaseModel):
    content: str
    post_id: int


class SearchComment(BaseModel):
    id: int


class SearchCommentFromPost(BaseModel):
    post_id: int


class SearchCommentFromUser(BaseModel):
    owner_id: int


class UpdateComment(BaseModel):
    id: int
    content: str
