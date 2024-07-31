from enum import Enum
from sqlalchemy import BigInteger, Integer, String, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped as M, mapped_column as mc
from .base import ModelBase


class OrgStatus(int, Enum):
    DISABLE = 0
    ENABLE = 1


class OrgUserStatus(int, Enum):
    DISABLE = 0
    ENABLE = 1


class Org(ModelBase):
    __tablename__ = "t_org"
    __table_args__ = (
        {"comment": "组织信息"}
    )

    org_id: M[int] = mc(BigInteger, primary_key=True, comment="组织ID")
    org_uuid: M[str] = mc(String(32), unique=True, comment="用户的uuid码")
    org_name: M[str] = mc(String(128), unique=True, comment="组织名称")
    owner_id: M[int] = mc(BigInteger, comment="组织所有者ID")
    is_admin: M[bool] = mc(SmallInteger, default=False, comment="是否为管理者组织")
    remark: M[str] = mc(String(256), default="", comment="组织备注信息")
    status: M[int] = mc(
        Integer, default=OrgStatus.ENABLE.value, comment="组织状态")
    deleted: M[bool] = mc(SmallInteger, default=False, comment="逻辑删除标识")


class OrgUser(ModelBase):
    __tablename__ = "t_org_user"
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uni_org_user"),
        {"comment": "组织用户信息"}
    )

    id: M[int] = mc(BigInteger, primary_key=True, comment="ID")
    user_id: M[int] = mc(BigInteger, comment="用户ID")
    org_id: M[int] = mc(BigInteger, comment="组织ID")
    user_name: M[str] = mc(String(128), comment="用户在组织内的名称")
    avatar: M[str] = mc(String(512), default="", comment="用户在组织内的头像")
    status: M[int] = mc(
        Integer, default=OrgUserStatus.ENABLE.value, comment="用户在组织内的状态")
