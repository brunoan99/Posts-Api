from pydantic import BaseModel

from datetime import datetime
from .user import ReturnUser
from .comment import Comment


class LikeComment(BaseModel):
    owner_id: int
    owner: ReturnUser
    comment_id: int
    comment: Comment
    created_at: datetime

    class Config:
        orm_mode = True


class CreateLikeComment(BaseModel):
    comment_id: int
