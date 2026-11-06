#!/usr/bin/env python3
# encoding: utf-8
"""初始化数据库 + 默认管理员

用法：
  python -m app.init_db          # 建表 + 建默认管理员（幂等）
  python -m app.init_db --reset  # 删库重建（★★ 会丢数据）
"""
import sys
from datetime import datetime

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User, ROLE_ADMIN
import app.models  # noqa: F401  确保所有模型被注册


def main(reset: bool = False):
    if reset:
        confirm = input("⚠️  这会删除所有数据，确认？输入 YES：")
        if confirm != "YES":
            print("已取消")
            return
        Base.metadata.drop_all(bind=engine)
        print("已删除旧表")

    Base.metadata.create_all(bind=engine)
    print("✅ 数据表已创建")

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.emp_no == settings.DEFAULT_ADMIN_ID).first()
        if admin:
            print(f"ℹ️  管理员 {settings.DEFAULT_ADMIN_ID} 已存在，跳过")
        else:
            admin = User(
                emp_no=settings.DEFAULT_ADMIN_ID,
                name=settings.DEFAULT_ADMIN_NAME,
                group_name="管理",
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                role=ROLE_ADMIN,
                joined_at=datetime.utcnow(),
            )
            db.add(admin)
            db.commit()
            print(f"✅ 默认管理员已创建")
            print(f"   工号: {settings.DEFAULT_ADMIN_ID}")
            print(f"   密码: {settings.DEFAULT_ADMIN_PASSWORD}")
            print(f"   ⚠️  上线务必改密码！")
    finally:
        db.close()

    print("\n下一步：")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("  打开 http://127.0.0.1:8000/docs 看接口文档")


if __name__ == "__main__":
    main(reset="--reset" in sys.argv)
