from typing import Any
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel
from sqlalchemy.orm import Session


class Rsp(BaseModel):
    """Restful API返回结果"""
    code: int = 0
    message: str = "Succeed"
    data: Any | None = None


@dataclass
class Jwt:
    """jwt相关信息"""
    # 用户uuid
    user_uuid: str
    # 组织uuid
    org_uuid: str | None = None
    # 是否管理者组织(默认False)
    org_is_admin: bool = False
    # 是否组织所有有者(默认False)
    org_owner: bool = False

    # 权限范围
    scope: list[str] | None = None


@dataclass
class Pagination:
    """分页读取信息"""
    page_idx: int = 1
    page_size: int = 10


@dataclass
class Actor:
    """操作信息"""
    session: Session
    user_uuid: str
    org_uuid: str | None = None
