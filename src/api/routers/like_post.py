from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse

from ..database import get_db
from .. import models, oauth2
from .. import models, oauth2
from ..schemas.like_post import LikePost, CreateLikePost
from ..schemas.general import Message
from ..schemas.user import ReturnUser

from sqlalchemy.orm import Session
from sqlalchemy import and_

from typing import List

router = APIRouter(
    prefix="/like/posts",
    tags=["Likes"]
)


#TODO TESTS
@router.put("", response_model=Message, responses={404: {"model": Message}})
def like_post_toggle(body: CreateLikePost, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):

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


#TODO TESTS 
@router.get("/{post_id}/{owner_id}", response_model=LikePost, responses={404, {"model": Message}})
def get_like(post_id: int, owner_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not comment:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Post with id: {post_id} was not found."})

    user = db.query(models.User).filter(models.User.id == owner_id).first()

    if not user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"User with id: {owner_id} was not found."})

    like = db.query(models.LikeComment).filter(and_(models.LikeComment.post_id == post_id, models.LikeComment.owner_id == owner_id)).first()

    if not like:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Like with post_id: {post_id} and owner_id: {owner_id} was not found"})
    return like


#TODO TESTS
@router.get("/{post_id}", response_model=List[LikePost])
def get_likes_from_post(post_id: int, db: Session = Depends(get_db)):    
    return db.query(models.LikePost).filter(models.LikePost.post_id == post_id).all()   


#TODO TESTS
@router.get("/user/{owner_id}", response_model=List[LikePost])
def get_likes_from_user(owner_id: int, db: Session = Depends(get_db)):
    return db.query(models.LikePost).filter(models.LikePost.owner_id == owner_id).all()   
