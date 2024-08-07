from enum import Enum
from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped as M, mapped_column as mc
from .base import ModelBase


class OrgStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class OrgUserStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class Org(ModelBase):
    __tablename__ = "t_org"
    __table_args__ = (
        {"comment": "组织信息"}
    )

    org_uuid: M[str] = mc(String(32), unique=True, comment="组织的uuid码")
    org_name: M[str] = mc(String(128), unique=True, comment="组织名称")
    owner_uuid: M[int] = mc(String(32), comment="组织所有者UUID")
    remark: M[str] = mc(String(256), default="", comment="组织备注信息")
    status: M[int] = mc(
        Integer, default=OrgStatus.ENABLE.value, comment="组织状态")
    is_admin: M[bool] = mc(Boolean, default=False, comment="是否为管理者组织")
    is_deleted: M[bool] = mc(Boolean, default=False, comment="逻辑删除标识")


class OrgUser(ModelBase):
    __tablename__ = "t_org_user"
    __table_args__ = (
        UniqueConstraint("org_uuid", "user_uuid", name="uni_org_user"),
        {"comment": "组织用户信息"}
    )

    org_uuid: M[int] = mc(String(32), comment="组织UUID")
    user_uuid: M[int] = mc(String(32), comment="用户UUID")
    user_name: M[str] = mc(String(128), comment="用户在组织内的名称")
    avatar: M[str] = mc(String(512), default="", comment="用户在组织内的头像")
    status: M[int] = mc(
        Integer, default=OrgUserStatus.ENABLE.value, comment="用户在组织内的状态")
