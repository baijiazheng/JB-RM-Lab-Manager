# encoding: utf-8
"""★ 分页工具

用法：
  items, total = paginate(db.query(Task), page=1, size=20)
  return ok({"items": [...], "total": total, "page": 1, "size": 20})
"""
from typing import Tuple, Any
from sqlalchemy.orm import Query


MAX_PAGE_SIZE = 100


def paginate(query: Query, page: int = 1, size: int = 20) -> Tuple[list, int]:
    page = max(1, page)
    size = max(1, min(size, MAX_PAGE_SIZE))
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return items, total


def page_meta(page: int, size: int, total: int) -> dict:
    pages = (total + size - 1) // size if size else 0
    return {"page": page, "size": size, "total": total, "pages": pages}
