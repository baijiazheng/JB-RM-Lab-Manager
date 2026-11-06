# encoding: utf-8
"""任务 + 提交 + 附件 接口"""
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, UploadFile as FastUploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.response import ok, fail
from app.core.deps import get_current_user, require_admin
from app.models.user import User, ROLE_ADMIN
from app.models.task import (
    Task, Submission, UploadFile as FileModel,
    TASK_PENDING, TASK_DOING, TASK_SUBMITTED, TASK_REJECTED, TASK_DONE,
)
from app.schemas.task import (
    TaskCreate, TaskStatusUpdate, SubmissionCreate,
    TaskOut, SubmissionOut, FileOut,
)

router = APIRouter(prefix="/tasks", tags=["任务"])

VALID_STATUS = {TASK_PENDING, TASK_DOING, TASK_SUBMITTED, TASK_REJECTED, TASK_DONE}


def _task_dict(t: Task) -> dict:
    d = TaskOut.model_validate(t).model_dump(mode="json")
    d["assignee_name"] = t.assignee.name if t.assignee else ""
    d["assignee_group"] = t.assignee.group_name if t.assignee else ""
    d["creator_name"] = t.creator.name if t.creator else ""
    d["submission_count"] = len(t.submissions)
    d["latest_submission_at"] = (
        t.submissions[-1].created_at.isoformat() if t.submissions else None)
    return d


# ---------- 队员：我的任务 ----------
@router.get("/mine")
def my_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ts = (db.query(Task).filter(Task.assignee_id == user.id)
          .order_by(Task.created_at.desc()).all())
    return ok([_task_dict(t) for t in ts])


@router.get("/{task_id}")
def task_detail(task_id: int, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return fail(404, "任务不存在", 404)
    if user.role != ROLE_ADMIN and t.assignee_id != user.id:
        return fail(403, "无权查看", 403)
    return ok(_task_dict(t))


@router.post("/{task_id}/submit")
def submit(task_id: int, body: SubmissionCreate, db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    """★ 提交任务（文字），任务状态自动变 submitted"""
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return fail(404, "任务不存在", 404)
    if t.assignee_id != user.id:
        return fail(403, "只能提交自己的任务", 403)
    if t.status in (TASK_DONE,):
        return fail(400, "任务已完成，不能再提交")

    s = Submission(task_id=task_id, user_id=user.id, content=body.content)
    db.add(s)
    t.status = TASK_SUBMITTED
    t.reject_reason = ""
    db.commit()
    db.refresh(s)
    return ok({"submission_id": s.id}, "已提交")


@router.get("/{task_id}/submissions")
def task_submissions(task_id: int, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return fail(404, "任务不存在", 404)
    if user.role != ROLE_ADMIN and t.assignee_id != user.id:
        return fail(403, "无权查看", 403)

    q = db.query(Submission).filter(Submission.task_id == task_id).order_by(
        Submission.created_at.desc())
    if user.role != ROLE_ADMIN:
        q = q.filter(Submission.user_id == user.id)

    out = []
    for s in q.all():
        d = SubmissionOut.model_validate(s).model_dump(mode="json")
        d["user_name"] = s.user.name if s.user else ""
        d["files"] = [FileOut.model_validate(f).model_dump(mode="json")
                      for f in s.files]
        out.append(d)
    return ok(out)


# ---------- 附件上传 ----------
@router.post("/submissions/{submission_id}/files")
async def upload_file(submission_id: int,
                      file: FastUploadFile = File(...),
                      db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    s = db.query(Submission).filter(Submission.id == submission_id).first()
    if not s:
        return fail(404, "提交记录不存在", 404)
    if s.user_id != user.id:
        return fail(403, "只能给自己的提交加附件", 403)

    # ★ 大小限制
    content = await file.read()
    size_mb = len(content) / 1024 / 1024
    if size_mb > settings.MAX_UPLOAD_MB:
        return fail(400, f"文件超过 {settings.MAX_UPLOAD_MB} MB")

    # ★ 防重命名：uuid + 原扩展名
    suffix = Path(file.filename or "").suffix[:16]
    stored = f"{uuid.uuid4().hex}{suffix}"
    dest = settings.UPLOAD_DIR / stored
    with open(dest, "wb") as f:
        f.write(content)

    fm = FileModel(
        submission_id=submission_id,
        original_name=(file.filename or stored)[:255],
        stored_name=stored,
        size_bytes=len(content),
    )
    db.add(fm)
    db.commit()
    db.refresh(fm)
    return ok(FileOut.model_validate(fm).model_dump(mode="json"), "上传成功")


@router.get("/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    from fastapi.responses import FileResponse
    fm = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not fm:
        return fail(404, "文件不存在", 404)
    path = settings.UPLOAD_DIR / fm.stored_name
    if not path.exists():
        return fail(404, "文件已丢失", 404)
    return FileResponse(path, filename=fm.original_name)


# ---------- 管理员：任务管理 ----------
@router.get("")
def list_all_tasks(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    ts = db.query(Task).order_by(Task.created_at.desc()).all()
    return ok([_task_dict(t) for t in ts])


@router.post("")
def create_task(body: TaskCreate, db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    assignee = db.query(User).filter(User.id == body.assignee_id).first()
    if not assignee:
        return fail(400, "指定的队员不存在")
    t = Task(
        title=body.title,
        description=body.description,
        requirement=body.requirement,
        deadline=body.deadline,
        assignee_id=body.assignee_id,
        creator_id=admin.id,
        status=TASK_PENDING,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return ok(_task_dict(t), "任务已发布")


@router.put("/{task_id}/status")
def update_status(task_id: int, body: TaskStatusUpdate,
                  db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """★ 审核：通过 → done；驳回 → rejected + 理由"""
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return fail(404, "任务不存在", 404)
    if body.status not in VALID_STATUS:
        return fail(400, f"状态必须是 {VALID_STATUS}")
    if body.status == TASK_REJECTED and not body.reject_reason.strip():
        return fail(400, "驳回必须填写理由")
    t.status = body.status
    t.reject_reason = body.reject_reason if body.status == TASK_REJECTED else ""
    db.commit()
    db.refresh(t)
    return ok(_task_dict(t), "状态已更新")


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db),
                _: User = Depends(require_admin)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return fail(404, "任务不存在", 404)
    db.delete(t)
    db.commit()
    return ok(None, "已删除")


# ---------- 管理员：所有提交 ----------
@router.get("/admin/submissions")
def all_submissions(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    q = db.query(Submission).order_by(Submission.created_at.desc())
    out = []
    for s in q.all():
        d = SubmissionOut.model_validate(s).model_dump(mode="json")
        d["user_name"] = s.user.name if s.user else ""
        d["task_title"] = s.task.title if s.task else ""
        d["files"] = [FileOut.model_validate(f).model_dump(mode="json")
                      for f in s.files]
        out.append(d)
    return ok(out)
