# encoding: utf-8
"""用户 Pydantic 模型（请求/响应校验）"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    emp_no: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
    emp_no: str


class UserCreate(BaseModel):
    emp_no: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=64)
    group_name: str = ""
    password: str = Field(..., min_length=6, max_length=128)
    role: str = "member"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    group_name: Optional[str] = None
    role: Optional[str] = None


class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    emp_no: str
    name: str
    group_name: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True
