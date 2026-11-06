# encoding: utf-8
"""用户管理（★ 仅管理员）

扩展提示：新增模块时，参照本文件新建 xxx.py，
然后在 api/__init__.py 里注册一行即可。
"""
from fastapi import APIRouter, Depends, UploadFile as FastUploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok, fail
from app.core.security import hash_password
from app.core.deps import require_admin
from app.core.pagination import paginate, page_meta
from app.models.user import User, ROLE_ADMIN, ROLE_MEMBER
from app.schemas.user import UserCreate, UserUpdate, PasswordReset, UserOut

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
def list_users(
    page: int = 1,
    size: int = 100,                    # 默认给大，前端下拉框要全量
    q: str = "",                        # 搜索：工号/姓名
    group_name: str = "",               # 筛组别
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """用户列表（支持分页 + 搜索 + 按组别筛选）"""
    query = db.query(User)
    if q:
        like = f"%{q}%"
        query = query.filter((User.emp_no.like(like)) | (User.name.like(like)))
    if group_name:
        query = query.filter(User.group_name == group_name)
    query = query.order_by(User.id)

    items, total = paginate(query, page, size)
    return ok({
        "items": [UserOut.model_validate(u).model_dump(mode="json") for u in items],
        **page_meta(page, size, total),
    })


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


@router.post("/import")
async def import_users(
    file: FastUploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """★ CSV 批量导入用户

    CSV 格式（第一行表头，UTF-8 编码，Excel 另存为 CSV 即可）：
        工号,姓名,组别,密码,角色
        2024001,张三,视觉,123456,member
        2024002,李四,机械,123456,member

    · 角色可选 member / admin，默认 member
    · 密码留空则默认 123456
    · 已存在的工号会跳过（不覆盖）
    """
    import csv, io

    raw = await file.read()
    # ★ 兼容 Excel 的 BOM
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = raw.decode("gbk")     # Windows Excel 默认可能是 GBK
        except UnicodeDecodeError:
            return fail(400, "文件编码不支持，请另存为 UTF-8 CSV")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return fail(400, "CSV 没有表头")

    created, skipped, errors = 0, 0, []
    for i, row in enumerate(reader, start=2):
        emp_no = (row.get("工号") or "").strip()
        name = (row.get("姓名") or "").strip()
        if not emp_no or not name:
            errors.append(f"第 {i} 行：工号或姓名为空")
            continue
        if db.query(User).filter(User.emp_no == emp_no).first():
            skipped += 1
            continue
        role = (row.get("角色") or "member").strip()
        if role not in (ROLE_ADMIN, ROLE_MEMBER):
            role = ROLE_MEMBER
        pwd = (row.get("密码") or "123456").strip() or "123456"
        db.add(User(
            emp_no=emp_no,
            name=name,
            group_name=(row.get("组别") or "").strip(),
            password_hash=hash_password(pwd),
            role=role,
        ))
        created += 1

    db.commit()
    return ok(
        {"created": created, "skipped": skipped, "errors": errors},
        f"导入完成：新增 {created}，跳过 {skipped}，错误 {len(errors)}",
    )


@router.get("/groups")
def list_groups(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """列出所有已用过的组别（给前端下拉框用）"""
    rows = db.query(User.group_name).distinct().all()
    return ok(sorted({r[0] for r in rows if r[0]}))
