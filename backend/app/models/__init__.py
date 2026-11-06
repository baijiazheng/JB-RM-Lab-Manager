# encoding: utf-8
"""★ 模型注册中心

新增模块时，在这里 import 一下，Alembic 才能检测到新表。
"""
from app.models.user import User, ROLE_ADMIN, ROLE_MEMBER
from app.models.task import (
    Task, Submission, UploadFile,
    TASK_PENDING, TASK_DOING, TASK_SUBMITTED, TASK_REJECTED, TASK_DONE,
)

__all__ = [
    "User", "ROLE_ADMIN", "ROLE_MEMBER",
    "Task", "Submission", "UploadFile",
    "TASK_PENDING", "TASK_DOING", "TASK_SUBMITTED", "TASK_REJECTED", "TASK_DONE",
]
