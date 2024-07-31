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
    user_uuid: str
    org_uuid: str | None = None

    # 后续需要移除
    org_id: int = 1


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
