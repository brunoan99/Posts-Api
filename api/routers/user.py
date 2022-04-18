from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse

from ..database import get_db
from .. import models, utils, oauth2
from ..schemas.user import User, CreateUser, UpdateUser, ReturnUser, ChangePassword
from ..schemas.general import Message

from sqlalchemy.orm import Session

from typing import List


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


def verify_if_new_email_actualy_in_use(email: str, db: Session):
    return db.query(models.User).filter(models.User.email == email).first() is not None


#TODO TESTS
@router.get("", response_model=List[ReturnUser])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


#TODO TESTS
@router.get("/{id}", response_model=ReturnUser, responses={404: {"model": Message}})
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f'user with id: {id} was not found.'})
    return user


#TODO TESTS
@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReturnUser, responses={409: {"model": Message}})
def create_user(body: CreateUser, db: Session = Depends(get_db)):
    if verify_if_new_email_actualy_in_use(body.email, db):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": f"user with email: {body.email} already exist."})
        
    body.password = utils.hash(body.password)    
    
    user = models.User(**body.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


#TODO TESTS
@router.put("", response_model=ReturnUser, responses={404: {"model": Message}, 409: {"model": Message}})
def update_user(body: UpdateUser, db: Session = Depends(get_db), current_user: User = Depends(oauth2.get_current_user)): 
    if verify_if_new_email_actualy_in_use(body.email, db):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": f"user with email: {body.email} already exist."})        
    
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user_query.update(body.dict(), synchronize_session=False)
    db.commit()
    return user_query.first()


#TODO TESTS
@router.put("/change-password", response_model=Message, responses={409: {"model": Message}, 401: {"model": Message}, 404: {"model": Message}})
def change_user_password(body: ChangePassword, db: Session = Depends(get_db), current_user: ReturnUser = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user = user_query.first()
    
    if not utils.verify(body.password, user.password):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "invalid credentials"})
    
    if body.new_password != body.new_password_confirm:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": "new password and confirmation not equal"})
    
    new_password = utils.hash(body.new_password)
    
    user_query.update({"password": new_password}, synchronize_session=False)
    db.commit()
    
    return {"message": f"password changed."}


#TODO TESTS
@router.delete("", response_model=Message, responses={404: {"model": Message}})
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(oauth2.get_current_user)):
    user_id = current_user.id
    
    user_query = db.query(models.User).filter(models.User.id == user_id)
    user_query.delete(synchronize_session=False)
    db.commit()

    return {"message": f"user with id: {user_id} was deleted."} 
