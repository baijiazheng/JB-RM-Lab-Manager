# encoding: utf-8
"""任务 Pydantic 模型"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    requirement: str = ""
    deadline: Optional[datetime] = None
    assignee_id: int


class TaskStatusUpdate(BaseModel):
    status: str
    reject_reason: str = ""


class SubmissionCreate(BaseModel):
    content: str = ""


class FileOut(BaseModel):
    id: int
    original_name: str
    size_bytes: float
    uploaded_at: datetime

    class Config:
        from_attributes = True


class SubmissionOut(BaseModel):
    id: int
    task_id: int
    user_id: int
    user_name: str = ""
    content: str
    created_at: datetime
    files: List[FileOut] = []

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    requirement: str
    deadline: Optional[datetime]
    status: str
    assignee_id: int
    assignee_name: str = ""
    assignee_group: str = ""
    creator_name: str = ""
    reject_reason: str
    created_at: datetime
    updated_at: datetime
    submission_count: int = 0
    latest_submission_at: Optional[datetime] = None

    class Config:
        from_attributes = True
