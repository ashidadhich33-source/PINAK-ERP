from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    display_name: Optional[str] = None
    mobile: Optional[str] = Field(None, regex="^[0-9]{10}$")
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    company_id: Optional[str] = None

class UserUpdate(UserBase):
    username: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    company_id: Optional[str]
    active: bool
    created_at: datetime
    
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