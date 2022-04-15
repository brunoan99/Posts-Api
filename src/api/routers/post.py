from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse

from ..database import get_db
from .. import models, oauth2
from ..schemas.post import Post, CreatePost, SearchPost, UpdatePost, ReturnPost
from ..schemas.user import ReturnUser
from ..schemas.general import Message

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_

from typing import List, Union, Optional


router = APIRouter(
    prefix="/post",
    tags=["Posts"]
)


#TODO TESTS
@router.get("s", response_model=List[ReturnPost])
def get_posts(db: Session = Depends(get_db), limit: Union[None, int] = None, search: Optional[str] = "", skip: int = 0):
    return db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).filter(or_(models.Post.title.contains(search), models.Post.content.contains(search))).join(models.LikePost, models.Post.id == models.LikePost.post_id, isouter=True).group_by(models.Post.id).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()


#TODO TESTS
@router.get("s/likes", response_model=List[ReturnPost])
def get_posts_most_likes(db: Session = Depends(get_db), limit: Union[None, int] = None, search: Optional[str] = "", skip: int = 0):
    return db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).filter(or_(models.Post.title.contains(search), models.Post.content.contains(search))).join(models.LikePost, models.Post.id == models.LikePost.post_id, isouter=True).group_by(models.Post.id).order_by(desc("likes"), models.Post.created_at.desc()).offset(skip).limit(limit).all()


#TODO TESTS
@router.get("s/latest", response_model=ReturnPost, responses={404: {"model": Message}})
def get_latest_post(db: Session = Depends(get_db), search: Optional[str] = "", skip: int = 0):
    
    post = db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).filter(or_(models.Post.title.contains(search), models.Post.content.contains(search))).join(models.LikePost, models.Post.id == models.LikePost.post_id, isouter=True).group_by(models.Post.id).order_by(models.Post.created_at.desc()).offset(skip).first()
    
    if not post:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "No posts yet."})
    return post


#TODO TESTS
@router.get("s/user/{owner_id}", response_model=List[ReturnPost])
def get_posts_from_user(owner_id: int, db: Session = Depends(get_db), limit: Union[None, int] = None, search: Optional[str] = "", skip: int = 0):  
    return db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).filter(and_(models.Post.owner_id == owner_id, or_(models.Post.title.contains(search), models.Post.content.contains(search)))).join(models.LikePost, models.Post.id == models.LikePost.post_id, isouter=True).group_by(models.Post.id).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()


#TODO TESTS
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_post(body: CreatePost, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    body = body.dict()
    body.update({"owner_id": current_user.id})
    
    post = models.Post(**body)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


#TODO TESTS
@router.get("/{post_id}", response_model=ReturnPost, responses={404: {"model": Message}})
def get_post(post_id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post, func.count(models.LikePost.post_id).label("likes")).filter(models.Post.id == post_id).join(models.LikePost, models.Post.id == models.LikePost.post_id, isouter=True).group_by(models.Post.id).first()
    
    if not post:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"post with id: {post_id} was not found."})
    return post


#TODO TESTS
@router.put("/", response_model=Post, responses={404: {"model": Message}, 401: {"model": Message}})
def update_post(body: UpdatePost, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == body.id)
    post: Post = post_query.first()
    
    if not post:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"post with id: {body.id} was not found."})
        
    if post.owner_id != current_user.id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": f'non authorized.'})    
    
    body = body.dict()
    body["title"] = post.title if body["title"] is None else body["title"]
    body["content"] = post.content if body["content"] is None else body["content"]
    body["published"] = post.published if body["published"] is None else body["published"]

    post_query.update(body, synchronize_session=False)
    db.commit()
    db.refresh(post)
    return post


#TODO TESTS
@router.delete("/", response_model=Message, responses={404: {"model": Message}, 401: {"model": Message}})
def delete_post(body: SearchPost, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == body.id)
    post = post_query.first()

    if not post:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f'post with id: {body.id} was not found.'})
        
    if post.owner_id != current_user.id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": f'non authorized.'})

    post_query.delete(synchronize_session=False)
    db.commit()

    return {"message": f"post with id: {body.id} was deleted"}
