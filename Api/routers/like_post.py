from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse

from ..database import get_db
from .. import models, oauth2
from .. import models, oauth2
from ..schemas.like_post import LikePost, CreateLikePost, CreateLikePostToggle, SearchLikeFromPost, SearchLikeFromUser
from ..schemas.general import Message
from ..schemas.user import ReturnUser

from sqlalchemy.orm import Session

from typing import List

router = APIRouter(
    prefix="/like/post",
    tags=["Likes"]
)


@router.put("", response_model=Message, responses={404: {"model": Message}, 409: {"model": Message}})
def like_post(body: CreateLikePost, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):

    comment = db.query(models.Comment).filter(models.Comment.id == body.post_id).first()

    if not comment: 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"message": f"post with id: {body.post_id} was not found."})    

    like_query = db.query(models.LikePost).filter(models.LikePost.post_id == body.post_id, models.LikePost.owner_id == current_user.id)

    if body.like == 1:
        if like_query.first() is None:
            like = models.LikePost(post_id = body.post_id, owner_id = current_user.id)
            db.add(like)
            db.commit()
            return {"message": f"Added like in post with id: {body.post_id}"}
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": f"Like in post with id: {body.post_id} already exist."})
    if like_query.first() is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Like in post with id: {body.post_id} not found"}) 
    like_query.delete(synchronize_session=False)
    db.commit()
    return {"message": f"Removed like in post with id: {body.post_id}"}


@router.put("/toggle", response_model=Message, responses={404: {"model": Message}})
def like_post_toggle(body: CreateLikePostToggle, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == body.post_id).first()

    if not post: 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"message": f"post with id: {body.post_id} was not found."})    

    like_query = db.query(models.LikePost).filter(models.LikePost.post_id == body.post_id, models.LikePost.owner_id == current_user.id)

    if not like_query.first():
        like = models.LikePost(post_id = body.post_id, owner_id = current_user.id)
        db.add(like)
        db.commit()
        return {"message": f"Added like in post with id: {body.post_id}"}
    like_query.delete(synchronize_session=False)
    db.commit()
    return {"message": f"Removed like in post with id: {body.post_id}"}


@router.get("s", response_model=List[LikePost])
def get_likes_from_post(body: SearchLikeFromPost, db: Session = Depends(get_db)):    
    return db.query(models.LikePost).filter(models.LikePost.post_id == body.post_id).all()   


@router.get("s/user", response_model=List[LikePost])
def get_likes_from_user(body: SearchLikeFromUser, db: Session = Depends(get_db)):
    return db.query(models.LikePost).filter(models.LikePost.owner_id == body.owner_id).all()   
