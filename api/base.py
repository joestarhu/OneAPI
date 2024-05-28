from typing import Generator
from fastapi import Query

from api.model.base import SessionLocal  # noqa


def get_db() -> Generator:
    """获取关系型数据库会话
    """
    with SessionLocal() as session:
        yield session


def get_page(page_idx: int = Query(default=1, description="页数"), page_size: int = Query(default=10, description="每页数量")) -> dict:
    """获取默认请求分页数据
    """
    return dict(page_idx=page_idx, page_size=page_size)
