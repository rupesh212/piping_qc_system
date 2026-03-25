from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.qa


class UserOut(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
