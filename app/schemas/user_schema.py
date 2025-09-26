from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, regex="^[0-9]{10,15}$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    company_id: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_superuser: bool
    is_active: bool
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: List[str] = []

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ACLPermission(BaseModel):
    menu_key: str
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_import: bool = False
    can_export: bool = False
    can_print: bool = False
    can_modify_past: bool = False
    is_admin: bool = False