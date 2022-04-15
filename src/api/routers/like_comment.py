from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse

from ..database import get_db
from .. import models, oauth2
from .. import models, oauth2
from ..schemas.like_comment import LikeComment, CreateLikeComment
from ..schemas.general import Message
from ..schemas.user import ReturnUser

from sqlalchemy.orm import Session

from typing import List

router = APIRouter(
    prefix="/like/comment",
    tags=["Likes"]
)


#TODO TESTS
@router.put("", response_model=Message, responses={404: {"model": Message}})
def like_comment_toggle(body: CreateLikeComment, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):

    comment = db.query(models.Comment).filter(models.Comment.id == body.comment_id).first()

    if not comment: 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"message": f"comment with id: {body.comment_id} was not found."})    

    like_query = db.query(models.LikeComment).filter(models.LikeComment.comment_id == body.comment_id, models.LikeComment.owner_id == current_user.id)

    if not like_query.first():
        like = models.LikeComment(comment_id = body.comment_id, owner_id = current_user.id)
        db.add(like)
        db.commit()
        return {"message": f"Added like in comment with id: {body.comment_id}"}
    like_query.delete(synchronize_session=False)
    db.commit()
    return {"message": f"Removed like in comment with id: {body.comment_id}"}


#TODO TESTS
@router.get("s/{comment_id}", response_model=List[LikeComment])
def get_likes_from_comment(comment_id: int, db: Session = Depends(get_db)):    
    return db.query(models.LikeComment).filter(models.LikeComment.comment_id == comment_id).all()   


#TODO TESTS
@router.get("s/user/{owner_id}", response_model=List[LikeComment])
def get_likes_from_user(owner_id: int, db: Session = Depends(get_db)):
    return db.query(models.LikeComment).filter(models.LikeComment.owner_id == owner_id).all()   
