from pydantic import BaseModel

from datetime import datetime
from .user import ReturnUser
from .post import Post


class LikePost(BaseModel):
    owner_id: int
    owner: ReturnUser
    post_id: int
    post: Post
    created_at: datetime

    class Config:
        orm_mode = True


class CreateLikePost(BaseModel):
    post_id: int
    like: int


class CreateLikePostToggle(BaseModel):
    post_id: int


class SearchLikeFromPost(BaseModel):
    post_id: int


class SearchLikeFromUser(BaseModel):
    owner_id: int
