from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from ..database import get_db
from .. import oauth2, models, utils
from ..schemas.auth import Token
from ..schemas.general import Message

from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Authentication"]
)


@router.post("/login", response_model=Token, responses={403: {"model": Message}})
def login(credentials: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):    
    user = db.query(models.User).filter(models.User.email == credentials.username).first()
    
    if user is None:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "invalid credentials"})
        
    if not utils.verify(credentials.password, user.password):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message", "invalid credentials"})
    
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    
    return {"access_token": access_token,
            "token_type": "bearer"}
