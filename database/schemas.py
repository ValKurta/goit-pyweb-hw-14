from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import Optional



class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)

class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: Optional[str]
    confirmed: bool

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class Enable2FAModel(BaseModel):
    user_id: int


class Login2FAModel(BaseModel):
    email: str
    password: str
    token: str

class RequestEmail(BaseModel):
    email: EmailStr
