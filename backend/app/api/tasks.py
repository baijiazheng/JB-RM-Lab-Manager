# encoding: utf-8
"""任务 + 提交 + 附件 接口"""
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, UploadFile as FastUploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.timeutil import to_local_str
from app.core.database import get_db
from app.core.response import ok, fail
from app.core.deps import get_current_user, require_admin
from app.core.pagination import paginate, page_meta
from app.models.user import User, ROLE_ADMIN
from app.models.task import (
    Task, Submission, UploadFile as FileModel,
    TASK_PENDING, TASK_DOING, TASK_SUBMITTED, TASK_REJECTED, TASK_DONE,
)
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskStatusUpdate, SubmissionCreate,
    TaskOut, SubmissionOut, FileOut, BatchTaskCreate,
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
        to_local_str(t.submissions[-1].created_at) if t.submissions else None)
    return d


# ---------- 队员：我的任务 ----------
@router.get("/mine")
def my_tasks(
    page: int = 1, size: int = 50,
    q: str = "", status: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """我的任务（支持分页 + 搜索 + 按状态筛选）"""
    query = db.query(Task).filter(Task.assignee_id == user.id)
    if q:
        like = f"%{q}%"
        query = query.filter((Task.title.like(like)) | (Task.description.like(like)))
    if status:
        query = query.filter(Task.status == status)
    query = query.order_by(Task.created_at.desc())

    items, total = paginate(query, page, size)
    return ok({
        "items": [_task_dict(t) for t in items],
        **page_meta(page, size, total),
    })


@router.get("/{task_id}")
def task_detail(task_id: int, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return fail(404, "任务不存在", 404)
    if user.role != ROLE_ADMIN and t.assignee_id != user.id:
        return fail(403, "无权查看", 403)
    return ok(_task_dict(t))


@router.put("/{task_id}/my-status")
def update_my_status(task_id: int, body: TaskStatusUpdate,
                     db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    """★ 队员自己标记进度（只能 pending <-> doing）"""
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return fail(404, "任务不存在", 404)
    if t.assignee_id != user.id:
        return fail(403, "只能改自己的任务", 403)
    if body.status not in (TASK_PENDING, TASK_DOING):
        return fail(400, "队员只能标记为 pending 或 doing")
    if t.status in (TASK_DONE, TASK_SUBMITTED):
        return fail(400, "已提交或已完成的任务不能改状态")
    t.status = body.status
    db.commit()
    db.refresh(t)
    return ok(_task_dict(t), "已更新")


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
def list_all_tasks(
    page: int = 1, size: int = 50,
    q: str = "", status: str = "", assignee_id: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """全部任务（分页 + 搜索 + 筛选）"""
    query = db.query(Task)
    if q:
        like = f"%{q}%"
        query = query.filter((Task.title.like(like)) | (Task.description.like(like)))
    if status:
        query = query.filter(Task.status == status)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    query = query.order_by(Task.created_at.desc())

    items, total = paginate(query, page, size)
    return ok({
        "items": [_task_dict(t) for t in items],
        **page_meta(page, size, total),
    })


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


@router.post("/batch")
def create_tasks_batch(body: BatchTaskCreate,
                       db: Session = Depends(get_db),
                       admin: User = Depends(require_admin)):
    """★ 批量发布：同一任务发给多个队员

    典型用法：「所有人看规则手册」→ 一次发给 30 人
    """
    ids = list(dict.fromkeys(body.assignee_ids))     # 去重保序
    if not ids:
        return fail(400, "至少选一个接收人")
    valid = {u.id for u in db.query(User).filter(User.id.in_(ids)).all()}
    missing = [i for i in ids if i not in valid]
    if missing:
        return fail(400, f"队员不存在: {missing}")

    created = 0
    for uid in ids:
        db.add(Task(
            title=body.title, description=body.description,
            requirement=body.requirement, deadline=body.deadline,
            assignee_id=uid, creator_id=admin.id, status=TASK_PENDING,
        ))
        created += 1
    db.commit()
    return ok({"created": created}, f"已发给 {created} 人")


@router.put("/{task_id}")
def update_task(task_id: int, body: TaskUpdate,
                db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """★ 编辑任务（标题/描述/要求/截止/接收人）"""
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return fail(404, "任务不存在", 404)
    data = body.model_dump(exclude_unset=True)
    if "assignee_id" in data:
        if not db.query(User).filter(User.id == data["assignee_id"]).first():
            return fail(400, "指定的队员不存在")
    for k, v in data.items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return ok(_task_dict(t), "已更新")


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
def all_submissions(page: int = 1, size: int = 50, q: str = "",
                    db: Session = Depends(get_db), _: User = Depends(require_admin)):
    query = db.query(Submission).order_by(Submission.created_at.desc())
    if q:
        query = query.filter(Submission.content.like(f"%{q}%"))
    items, total = paginate(query, page, size)
    out = []
    for s in items:
        d = SubmissionOut.model_validate(s).model_dump(mode="json")
        d["user_name"] = s.user.name if s.user else ""
        d["task_title"] = s.task.title if s.task else ""
        d["files"] = [FileOut.model_validate(f).model_dump(mode="json")
                      for f in s.files]
        out.append(d)
    return ok({"items": out, **page_meta(page, size, total)})
