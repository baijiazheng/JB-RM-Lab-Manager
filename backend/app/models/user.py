# encoding: utf-8
"""用户模型"""
from app.core.timeutil import utcnow
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

ROLE_ADMIN = "admin"
ROLE_MEMBER = "member"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    emp_no = Column(String(32), unique=True, index=True, nullable=False)  # 工号（登录账号）
    name = Column(String(64), nullable=False)                             # 姓名
    group_name = Column(String(32), default="")                           # 组别：视觉/机械/电控...
    password_hash = Column(String(255), nullable=False)
    role = Column(String(16), default=ROLE_MEMBER, nullable=False)        # admin / member
    joined_at = Column(DateTime, default=utcnow)                 # 加入时间
