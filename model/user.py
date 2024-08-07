from enum import Enum
from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped as M, mapped_column as mc
from .base import ModelBase


class UserStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class UserAuthType(Enum):
    PASSWORD = 0
    DINGTALK = 1


class User(ModelBase):
    __tablename__ = "t_user"
    __table_args__ = (
        {"comment": "用户信息"}
    )
    user_uuid: M[str] = mc(String(32), unique=True, comment="用户UUID")
    account: M[str] = mc(String(128), unique=True, comment="用户账户,唯一")
    phone: M[str] = mc(String(256), unique=True, comment="用户手机号,加密存储")
    nick_name: M[str] = mc(String(128), comment="用户昵称")
    avatar: M[str] = mc(String(512), default="", comment="用户头像地址")
    status: M[int] = mc(
        Integer, default=UserStatus.ENABLE.value, comment="用户状态")
    is_deleted: M[bool] = mc(Boolean, default=False, comment="逻辑删除标识")


class UserAuth(ModelBase):
    __tablename__ = "t_user_auth"
    __table_args__ = (
        UniqueConstraint("user_uuid", "auth_type", "auth_identify",
                         name="uni_user_auth"),
        {"comment": "用户认证信息"}
    )
    user_uuid: M[str] = mc(String(32), comment="用户UUID")
    auth_type: M[int] = mc(
        Integer, default=UserAuthType.PASSWORD.value, comment="认证类型")
    auth_identify: M[str] = mc(
        String(128), default="", comment="认证标识,比如appid,appkey等")
    auth_value: M[str] = mc(String(256), comment="认证值")
