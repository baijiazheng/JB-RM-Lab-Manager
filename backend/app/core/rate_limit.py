# encoding: utf-8
"""★ 简单登录限流（内存版，够用；多进程部署要换 Redis）"""
import time
from collections import defaultdict
from threading import Lock

from app.core.config import settings

_attempts: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def _clean(key: str, now: float) -> None:
    window_start = now - settings.LOGIN_WINDOW_SECONDS
    _attempts[key] = [t for t in _attempts[key] if t > window_start]


def is_blocked(key: str) -> bool:
    """key 一般是 工号 或 IP"""
    now = time.time()
    with _lock:
        _clean(key, now)
        return len(_attempts[key]) >= settings.LOGIN_MAX_ATTEMPTS


def record_failure(key: str) -> None:
    now = time.time()
    with _lock:
        _clean(key, now)
        _attempts[key].append(now)


def reset(key: str) -> None:
    """登录成功后清空"""
    with _lock:
        _attempts.pop(key, None)


def remaining_seconds(key: str) -> int:
    now = time.time()
    with _lock:
        _clean(key, now)
        if not _attempts[key]:
            return 0
        oldest = min(_attempts[key])
        return max(0, int(settings.LOGIN_WINDOW_SECONDS - (now - oldest)))
