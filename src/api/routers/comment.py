from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse

from ..database import get_db
from .. import models, oauth2
from ..schemas.comment import Comment, CreateComment, SearchComment, UpdateComment, ReturnComment
from ..schemas.general import Message
from ..schemas.user import ReturnUser

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from typing import List, Union, Optional

router = APIRouter(
    prefix="/comment",
    tags=["Comments"]
)


#TODO TESTS
@router.get("s", response_model=List[ReturnComment])
def get_comments(db: Session = Depends(get_db), limit: Union[None, int] = None, search: Optional[str] = "", skip: int = 0):
    print(f'limit: {limit}, search: {search}, skip: {skip}')
    return db.query(models.Comment, func.count(models.Comment.id).label("likes")).filter(models.Comment.content.contains(search)).join(models.LikeComment, models.Comment.id == models.LikeComment.comment_id, isouter=True).group_by(models.Comment.id).order_by(models.Comment.created_at.desc()).offset(skip).limit(limit).all()



#TODO TESTS
@router.get("s/post/{post_id}", response_model=List[ReturnComment])
def get_comments_from_post(post_id: int, db: Session = Depends(get_db), limit: Union[None, int] = None, search: Optional[str] = "", skip: int = 0):
    return db.query(models.Comment, func.count(models.Comment.id).label("likes")).filter(and_(models.Comment.post_id == post_id, models.Comment.content.contains(search))).join(models.LikeComment, models.Comment.id == models.LikeComment.comment_id, isouter=True).group_by(models.Comment.id).order_by(models.Comment.created_at.desc()).offset(skip).limit(limit).all()


#TODO TESTS
@router.get("s/user/{owner_id}", response_model=List[ReturnComment])
def get_comments_from_user(owner_id: int, db: Session = Depends(get_db), limit: Union[None, int] = None, search: Optional[str] = "", skip: int = 0):    
    return db.query(models.Comment, func.count(models.Comment.id).label("likes")).filter(and_(models.Comment.owner_id == owner_id, models.Comment.content.contains(search))).join(models.LikeComment, models.Comment.id == models.LikeComment.comment_id, isouter=True).group_by(models.Comment.id).order_by(models.Comment.created_at.desc()).offset(skip).limit(limit).all()


#TODO TESTS
@router.get("/{id}", response_model=ReturnComment, responses={404: {"model": Message}})
def get_comment(id: int, db: Session = Depends(get_db)):

    comment = db.query(models.Comment, func.count(models.LikeComment.comment_id).label("likes")).filter(models.Comment.id == id).join(models.LikeComment, models.Comment.id == models.LikeComment.comment_id, isouter=True).group_by(models.Comment.id).first()

    if not comment: 
         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"comment with id: {id} was not found."})

    return comment


#TODO TESTS
@router.post("", status_code=status.HTTP_201_CREATED, response_model=Comment)
def create_comment(body: CreateComment, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    body = body.dict()
    body.update({"owner_id": current_user.id})

    comment = models.Comment(**body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


#TODO TESTS
@router.put("", response_model=Comment, responses={404: {"model": Message}, 401: {"model": Message}})
def update_comment(body: UpdateComment, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    print(body.id)
    body = body.dict()
    comment_query = db.query(models.Comment).filter(models.Comment.id == body['id'])
    comment = comment_query.first()

    if not comment: 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"comment with id: {body['id']} was not found."})

    if comment.owner_id != current_user.id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": f"non authorized."})

    comment_query.update(body, synchronize_session=False)
    db.commit()
    db.refresh(comment)
    return comment


#TODO TESTS
@router.delete("", response_model=Message, responses={404: {"model": Message}, 401: {"model": Message}})
def delete_comment(body: SearchComment, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comment).filter(models.Comment.id == body['id'])
    comment = comment_query.first()

    if not comment:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"comment with id: {body['id']} was not found."})

    if comment.owner_id != current_user.id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": f"non authorized."})

    comment_query.delete(synchronize_session=False)
    db.commit()

    return {"message": f"comment with id: {body['id']} was deleted"}
