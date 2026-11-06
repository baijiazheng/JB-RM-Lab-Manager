# encoding: utf-8
"""用户管理（★ 仅管理员）

扩展提示：新增模块时，参照本文件新建 xxx.py，
然后在 api/__init__.py 里注册一行即可。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok, fail
from app.core.security import hash_password
from app.core.deps import require_admin
from app.models.user import User, ROLE_ADMIN, ROLE_MEMBER
from app.schemas.user import UserCreate, UserUpdate, PasswordReset, UserOut

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).order_by(User.id).all()
    return ok([UserOut.model_validate(u).model_dump(mode="json") for u in users])


@router.post("")
def create_user(body: UserCreate, db: Session = Depends(get_db),
                _: User = Depends(require_admin)):
    if body.role not in (ROLE_ADMIN, ROLE_MEMBER):
        return fail(400, "角色只能是 admin 或 member")
    if db.query(User).filter(User.emp_no == body.emp_no).first():
        return fail(400, "工号已存在")
    u = User(
        emp_no=body.emp_no,
        name=body.name,
        group_name=body.group_name,
        password_hash=hash_password(body.password),
        role=body.role,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return ok(UserOut.model_validate(u).model_dump(mode="json"), "创建成功")


@router.put("/{user_id}")
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db),
                _: User = Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return fail(404, "用户不存在", 404)
    if body.name is not None:
        u.name = body.name
    if body.group_name is not None:
        u.group_name = body.group_name
    if body.role is not None:
        if body.role not in (ROLE_ADMIN, ROLE_MEMBER):
            return fail(400, "角色只能是 admin 或 member")
        u.role = body.role
    db.commit()
    db.refresh(u)
    return ok(UserOut.model_validate(u).model_dump(mode="json"), "已更新")


@router.post("/{user_id}/reset-password")
def reset_password(user_id: int, body: PasswordReset, db: Session = Depends(get_db),
                   _: User = Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return fail(404, "用户不存在", 404)
    u.password_hash = hash_password(body.new_password)
    db.commit()
    return ok(None, "密码已重置")


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                cur: User = Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return fail(404, "用户不存在", 404)
    if u.id == cur.id:
        return fail(400, "不能删除自己")
    db.delete(u)
    db.commit()
    return ok(None, "已删除")
