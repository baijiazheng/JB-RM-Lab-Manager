# encoding: utf-8
"""★ 依赖注入：当前用户 / 权限校验"""
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.core.response import fail
from app.models.user import User, ROLE_ADMIN


class AuthError(Exception):
    """自定义认证异常，由 main.py 统一处理"""
    def __init__(self, msg="未登录或登录已过期", code=401):
        self.msg = msg
        self.code = code


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    """从 Authorization: Bearer <token> 里解析当前用户"""
    if not authorization.startswith("Bearer "):
        raise AuthError("缺少 token")
    token = authorization[7:]
    payload = decode_token(token)
    if not payload:
        raise AuthError("token 无效或已过期")
    emp_no = payload.get("sub")
    user = db.query(User).filter(User.emp_no == emp_no).first()
    if not user:
        raise AuthError("用户不存在")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """管理员专用"""
    if user.role != ROLE_ADMIN:
        raise AuthError("需要管理员权限", code=403)
    return user
