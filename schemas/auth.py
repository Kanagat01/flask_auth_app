from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

from models import User


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    password: str


class UserLoginSchema(BaseModel):
    login: EmailStr | str
    password: str


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class UserPasswordResetSchema(BaseModel):
    login: str


class UserPasswordResetConfirmSchema(BaseModel):
    token: str
    new_password: str
