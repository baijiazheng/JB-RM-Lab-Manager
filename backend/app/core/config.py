# encoding: utf-8
"""全局配置（★ 单独拎出来，改这里不改代码）"""
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # --- 应用 ---
    APP_NAME: str = "RM 战队实验室管理后台"
    API_PREFIX: str = "/api"

    # --- 数据库 ---
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/rm_lab.db"

    # --- JWT（★ 上线务必改 SECRET_KEY）---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_please_use_a_long_random_string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12       # 12 小时

    # --- 文件上传 ---
    UPLOAD_DIR: Path = BASE_DIR / "static" / "uploads"
    MAX_UPLOAD_MB: int = 50

    # --- 登录限流 ---
    LOGIN_MAX_ATTEMPTS: int = 5                      # 5 次
    LOGIN_WINDOW_SECONDS: int = 300                  # 5 分钟内

    # --- 默认管理员 ---
    DEFAULT_ADMIN_ID: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "123456"
    DEFAULT_ADMIN_NAME: str = "系统管理员"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# 确保上传目录存在
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
