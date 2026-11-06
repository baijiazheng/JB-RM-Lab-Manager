# encoding: utf-8
"""任务 / 提交 / 附件模型"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Float
)
from sqlalchemy.orm import relationship
from app.core.database import Base

# 任务状态
TASK_PENDING = "pending"      # 未开始
TASK_DOING = "doing"          # 进行中
TASK_SUBMITTED = "submitted"  # 已提交（待审核）
TASK_REJECTED = "rejected"    # 已驳回
TASK_DONE = "done"            # 已完成


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, default="")                    # 任务描述
    requirement = Column(Text, default="")                    # 要求
    deadline = Column(DateTime, nullable=True)                # 截止时间
    status = Column(String(16), default=TASK_PENDING, nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reject_reason = Column(Text, default="")                  # 驳回理由
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[creator_id])
    submissions = relationship("Submission", back_populates="task",
                               cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, default="")                        # 文字提交内容
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="submissions")
    user = relationship("User")
    files = relationship("UploadFile", back_populates="submission",
                         cascade="all, delete-orphan")


class UploadFile(Base):
    """★ 注意：叫 UploadFile 会和 fastapi.UploadFile 撞名，导入时用 alias"""
    __tablename__ = "upload_files"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    original_name = Column(String(255), nullable=False)       # 原始文件名（给用户看）
    stored_name = Column(String(255), nullable=False)         # 磁盘上防重名的名字
    size_bytes = Column(Float, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission", back_populates="files")
