from sqlalchemy import BigInteger, Boolean, SmallInteger, String, UniqueConstraint, select, and_
from sqlalchemy.orm import Mapped as M, mapped_column as mc
from jhu.orm import ORM, ORMCheckRule
from .base import ModelBase


class OrgSettings:
    STATUS_DISABLE: int = 0
    STATUS_ENABLE: int = 1

    ORG_USER_STATUS_DISABLE: int = 0
    ORG_USER_STATUS_ENABLE: int = 1


class Org(ModelBase):
    __tablename__ = "t_org"
    __table_args__ = (
        {"comment": "组织信息"}
    )

    org_name: M[str] = mc(String(128), unique=True, comment="组织名称,全局唯一")
    owner_id: M[int] = mc(BigInteger, comment="组织所有者ID")
    status: M[int] = mc(
        SmallInteger, default=OrgSettings.STATUS_ENABLE, comment="组织状态")
    is_admin: M[bool] = mc(Boolean, default=False, comment="平台组织标识")
    remark: M[str] = mc(String(256), comment="组织备注")
    deleted: M[bool] = mc(Boolean, default=False, comment="逻辑删除标志,True表示逻辑已删除")


class OrgUser(ModelBase):
    __tablename__ = "t_org_user"
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uni_org_user"),
        {"comment": "组织用户"}
    )

    org_id: M[int] = mc(BigInteger, comment="组织ID")
    user_id: M[int] = mc(BigInteger, comment="用户ID")
    user_name: M[str] = mc(String(256), comment="组织用户名,默认取用户昵称")
    status: M[int] = mc(
        SmallInteger, default=OrgSettings.ORG_USER_STATUS_ENABLE, comment="组织用户状态")
