from sqlalchemy import BigInteger, Boolean, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped as M, mapped_column as mc
from api.model.base import ModelBase  # noqa


class OrgSettings:
    """组织配置
    """
    # 组织状态:停用
    STATUS_DISABLE: int = 0
    # 组织状态:启用
    STATUS_ENABLE: int = 1

    # 组织用户状态
    USER_STATUS_DISABLE: int = 0
    USER_STATUS_ENABLE: int = 1


class Org(ModelBase):
    __tablename__ = "t_org"
    __table_args__ = (
        {"comment": "组织信息"}
    )

    name: M[str] = mc(String(64), unique=True, comment="组织名称")
    remark: M[str] = mc(String(256), comment="组织描述")
    owner_id: M[int] = mc(BigInteger, comment="组织所有者ID")
    status: M[int] = mc(
        SmallInteger, default=OrgSettings.STATUS_ENABLE, comment="组织状态")
    deleted: M[bool] = mc(Boolean, default=False, comment="逻辑删除标识")
    is_admin: M[bool] = mc(Boolean, default=False, comment="平台组织标识")


class OrgUser(ModelBase):
    __tablename__ = "t_org_user"
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uni_org_user"),
        {"comment": "组织用户信息"}
    )

    org_id: M[int] = mc(BigInteger, comment="组织ID")
    user_id: M[int] = mc(BigInteger, comment="用户ID")
    status: M[int] = mc(
        SmallInteger, default=OrgSettings.USER_STATUS_ENABLE, comment="组织用户状态")
