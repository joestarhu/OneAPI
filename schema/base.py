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
    user_id: int
    org_id: int

    @property
    def create_info(self) -> dict:
        user_id = self.user_id
        dt = datetime.now()
        return dict(create_id=user_id,
                    update_id=user_id,
                    create_dt=dt,
                    update_dt=dt)

    @property
    def update_info(self) -> dict:
        user_id = self.user_id
        dt = datetime.now()
        return dict(update_id=user_id,
                    update_dt=dt)
