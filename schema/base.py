from dataclasses import dataclass
from sqlalchemy.orm import Session


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
    scopes: list[str] | None = None


@dataclass
class Pagination:
    """分页读取信息"""
    page_idx: int = 1
    page_size: int = 10


@dataclass
class Actor:
    """操作用户信息"""
    # 数据库会话
    session: Session

    # 操作用户的UUID
    user_uuid: str

    # 操作用户选择的组织UUID
    org_uuid: str | None = None

    # 操作用户是否为组织所有者,即组织的超级管理员
    is_org_owner: bool = False


# @dataclass
# class Actor:
#     """操作信息"""
#     session: Session
#     user_uuid: str
#     org_uuid: str | None = None
#     org_is_admin: bool = False

#     org_owner: bool = False
#     scopes: list[str] | None = None
