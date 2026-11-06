# encoding: utf-8
"""★★★ 应用入口

职责只有三件：
  ① 创建 FastAPI app
  ② 挂 CORS / 静态文件 / 全局异常处理
  ③ 把 api/__init__.py 里注册的 routers 全部挂上
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.response import ok, fail
from app.core.deps import AuthError
from app.api import routers

app = FastAPI(title=settings.APP_NAME, version="1.0.0",
              docs_url="/docs", redoc_url="/redoc")

# ---------- CORS（本地开发：允许 Vite 的 5173）----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 静态文件（附件下载 / 头像等）----------
app.mount("/static", StaticFiles(directory=str(settings.UPLOAD_DIR.parent)), name="static")


# ---------- ★ 全局统一错误处理 ----------
@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    return fail(exc.code, exc.msg, exc.code if exc.code in (401, 403) else 400)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return fail(exc.status_code, str(exc.detail), exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # 把 pydantic 的错误压成一句话
    first = exc.errors()[0] if exc.errors() else {}
    loc = ".".join(str(x) for x in first.get("loc", []) if x != "body")
    msg = f"参数错误: {loc} - {first.get('msg', '')}"
    return fail(422, msg, 422)


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return fail(500, f"服务器内部错误: {exc}", 500)


# ---------- 注册所有路由 ----------
for r in routers:
    app.include_router(r, prefix=settings.API_PREFIX)


# ---------- 健康检查 ----------
@app.get("/api/health")
def health():
    return ok({"status": "ok", "app": settings.APP_NAME})


@app.get("/")
def root():
    return ok({"msg": "RM 战队实验室管理后台 API", "docs": "/docs"})
