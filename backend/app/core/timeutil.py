# encoding: utf-8
"""★ 时区工具：数据库存 UTC，输出转北京时间

设计：
  · 数据库统一存 UTC（datetime.utcnow）—— 避免夏令时/跨时区问题
  · 输出给前端时转成 Asia/Shanghai（北京时间）
  · 前端直接显示字符串即可

这样前端不用管时区，后端统一处理。
"""
from datetime import datetime, timezone, timedelta

# 北京时间（UTC+8）
CST = timezone(timedelta(hours=8))


def utcnow() -> datetime:
    """统一用这个代替 datetime.utcnow()"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_local_str(dt: datetime | None) -> str | None:
    """UTC datetime → 北京时间的 ISO 字符串（无时区后缀，前端直接显示）"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(CST).strftime("%Y-%m-%dT%H:%M:%S")


def local_str_to_utc(dt: datetime | None) -> datetime | None:
    """北京时间 → UTC（存库前调用）

    前端传的时间是北京时间（用户输入 18:00 就是下午 6 点）
    → 存库要转成 UTC（10:00）
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CST)     # 当作北京时间
    return dt.astimezone(timezone.utc).replace(tzinfo=None)
