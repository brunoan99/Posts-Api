from typing import List
from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, oauth2
from ..schemas.comment import Comment, CreateComment, SearchComment, UpdateComment, SearchCommentFromPost, SearchCommentFromUser, CommentFromPost, CommentFromUser
from ..schemas.general import Message
from ..schemas.user import ReturnUser



router = APIRouter(
    prefix="/comment",
    tags=["Comments"]
)


@router.get("", response_model=Comment, responses={404: {"model": Message}})
def get_comment(body: SearchComment, db: Session = Depends(get_db)):
    print(body.dict())

    comment = db.query(models.Comment).filter(models.Comment.id == body.id).first()

    if not comment: 
         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"comment with id: {body.id} was not found."})

    return comment


@router.post("", response_model=Comment)
def create_comment(body: CreateComment, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    body = body.dict()
    body.update({"owner_id": current_user.id})

    comment = models.Comment(**body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.put("", response_model=Comment, responses={404: {"model": Message}, 401: {"model": Message}})
def update_comment(body: UpdateComment, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    print(body.id)
    body = body.dict()
    comment_query = db.query(models.Comment).filter(models.Comment.id == body['id'])
    comment = comment_query.first()

    if not comment: 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"comment with id: {body['id']} was not found."})

    if comment.owner_id != current_user.id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": f""})

    comment_query.update(body, synchronize_session=False)
    db.commit()
    db.refresh(comment)
    return comment


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


@router.get("s/post", response_model=List[CommentFromPost])
def get_comments_from_post(body: SearchCommentFromPost, db: Session = Depends(get_db)):    
    comments = db.query(models.Comment).filter(models.Comment.post_id == body.post_id).all()

    return comments


@router.get("s/user", response_model=List[CommentFromUser])
def get_comments_from_post(body: SearchCommentFromUser, db: Session = Depends(get_db)):    
    comments = db.query(models.Comment).filter(models.Comment.owner_id == body.owner_id).all()

    return comments
