# encoding: utf-8
"""★ 全局统一返回格式

所有接口返回：
  { "code": 0, "msg": "ok", "data": ... }
code = 0 表示成功，非 0 表示业务错误
"""
from typing import Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def ok(data: Any = None, msg: str = "ok") -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({"code": 0, "msg": msg, "data": data}),
    )


def fail(code: int = 1, msg: str = "error", http_status: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=http_status,
        content={"code": code, "msg": msg, "data": None},
    )
