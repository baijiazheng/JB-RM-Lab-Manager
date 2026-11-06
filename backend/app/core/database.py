# encoding: utf-8
"""数据库连接与 Session 管理"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# SQLite 需要 check_same_thread=False（FastAPI 多线程）
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI 依赖：每个请求一个 Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
