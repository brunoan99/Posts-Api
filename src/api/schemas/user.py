from datetime import datetime
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    email: EmailStr
    password: str    
    created_at: datetime
        
    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    email: EmailStr
    password: str


class UpdateUser(BaseModel):
    email: EmailStr


class ReturnUser(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        orm_mode = True


class ReturnUserComment(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        orm_mode = True


class ChangePassword(BaseModel):
    password: str
    new_password: str
    new_password_confirm: str
