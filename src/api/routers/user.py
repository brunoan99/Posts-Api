from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse

from ..database import get_db
from .. import models, utils, oauth2
from ..schemas.user import User, CreateUser, SearchUser, UpdateUser, ReturnUser, ChangePassword
from ..schemas.general import Message

from sqlalchemy.orm import Session

from typing import List


router = APIRouter(
    prefix="/user",
    tags=["Users"]
)


@router.get("s", response_model=List[ReturnUser])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/", response_model=ReturnUser, responses={404: {"model": Message}})
def get_user(body: SearchUser, db: Session = Depends(get_db)):
    user_id = body.id
    
    user = db.query(models.User).filter(models.User.id == user_id)
    
    if not user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f'user with id: {user_id} was not found.'})
    return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReturnUser, responses={409: {"model": Message}})
def create_user(body: CreateUser, db: Session = Depends(get_db)):
    user_email = body.email
    
    body.password = utils.hash(body.password)
    
    user_query = db.query(models.User).filter(models.User.email == user_email)
        
    if user_query.first():
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": f"user with email: {user_email} already exist."})
    
    user = models.User(**body.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/", response_model=ReturnUser, responses={404: {"model": Message}, 409: {"model": Message}})
def update_user(body: UpdateUser, db: Session = Depends(get_db), current_user: User = Depends(oauth2.get_current_user)):
    user_id = body.id
    
    user_query = db.query(models.User).filter(models.User.id == user_id)

    if body.id != current_user.id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": f"non authorized."})

    if not user_query.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"user with id: {user_id} was not found."})
    
    another_user_with_same_email = db.query(models.User).filter(models.User.email == body.email).first()
    
    if another_user_with_same_email is not None:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": f"user with email: {body.email} already exist."})
        
    user_query.update(body.dict(), synchronize_session=False)
    db.commit()
     
    return user_query.first()


@router.delete("/", response_model=Message, responses={404: {"model": Message}})
def delete_user(body: SearchUser, db: Session = Depends(get_db), current_user: User = Depends(oauth2.get_current_user)):
    user_id = body.id

    user_query = db.query(models.User).filter(models.User.id == user_id)

    if body.id != current_user.id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": f"non authorized."})

    if not user_query.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"user with id: {user_id} was not found."})

    user_query.delete(synchronize_session=False)
    db.commit()

    return {"message": f"user with id: {user_id} was deleted."}


@router.put("/change-password", response_model=Message, responses={409: {"model": Message}, 401: {"model": Message}, 404: {"model": Message}})
def change_user_password(body: ChangePassword, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
        
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user = user_query.first()
    
    if not user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f'user with id: {current_user.id} was not found.'})
    
    if not utils.verify(body.password, user.password):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "invalid credentials"})
    
    if body.new_password != body.new_password_confirm:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": "new password and confirmation not equal"})
    
    
    new_password = utils.hash(body.new_password)
    user_query.update({"password": new_password}, synchronize_session=False)
    db.commit()
    
    return {"message": f"password changed."}
