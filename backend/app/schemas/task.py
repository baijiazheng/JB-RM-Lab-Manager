# encoding: utf-8
"""任务 Pydantic 模型"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer, field_validator
from app.core.timeutil import to_local_str, local_str_to_utc


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    requirement: str = ""
    deadline: Optional[datetime] = None
    assignee_id: int

    @field_validator("deadline")
    @classmethod
    def _deadline_to_utc(cls, v):
        return local_str_to_utc(v)


class TaskUpdate(BaseModel):
    """编辑任务（全部可选）"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirement: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None

    @field_validator("deadline")
    @classmethod
    def _deadline_to_utc(cls, v):
        return local_str_to_utc(v)


class BatchTaskCreate(BaseModel):
    """批量发布：同一任务发给多个队员"""
    title: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    requirement: str = ""
    deadline: Optional[datetime] = None
    assignee_ids: List[int] = Field(..., min_length=1)

    @field_validator("deadline")
    @classmethod
    def _deadline_to_utc(cls, v):
        return local_str_to_utc(v)


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

    @field_serializer("uploaded_at")
    def _ser_file_time(self, v):
        return to_local_str(v)


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

    @field_serializer("created_at")
    def _ser_sub_time(self, v):
        return to_local_str(v)


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

    @field_serializer("deadline", "created_at", "updated_at", "latest_submission_at")
    def _ser_task_time(self, v):
        return to_local_str(v)
