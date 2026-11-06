# encoding: utf-8
"""认证接口：登录 / 当前用户信息"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok, fail
from app.core.security import verify_password, create_access_token
from app.core.rate_limit import is_blocked, record_failure, reset, remaining_seconds
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import LoginRequest, UserOut

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """★ 工号 + 密码登录，返回 JWT"""
    key = body.emp_no
    if is_blocked(key):
        return fail(429, f"尝试次数过多，请 {remaining_seconds(key)} 秒后再试", 429)

    user = db.query(User).filter(User.emp_no == body.emp_no).first()
    if not user or not verify_password(body.password, user.password_hash):
        record_failure(key)
        return fail(400, "工号或密码错误", 400)

    reset(key)
    token = create_access_token(user.emp_no, user.role)
    return ok({
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "name": user.name,
        "emp_no": user.emp_no,
    }, "登录成功")


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return ok(UserOut.model_validate(user).model_dump(mode="json"))
