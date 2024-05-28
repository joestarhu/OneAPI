from sqlalchemy import BigInteger, Boolean, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped as M, mapped_column as mc
from api.model.base import ModelBase  # noqa


class UserSettings:
    """用户配置
    """

    # 用户状态:停用
    STATUS_DISABLE: int = 0
    # 用户状态:启用
    STATUS_ENABLE: int = 1

    # 用户认证类型:密码
    AUTH_TYPE_PASSWORD: int = 0


class User(ModelBase):
    __tablename__ = "t_user"
    __table_args__ = (
        {"comment": "用户信息"}
    )

    account: M[str] = mc(String(128), unique=True, comment="用户账户,全局唯一")
    phone: M[str] = mc(String(256), unique=True, comment="用户手机号,全局唯一,加密存储")
    nick_name: M[str] = mc(String(128), comment="用户昵称")
    status: M[int] = mc(
        SmallInteger, default=UserSettings.STATUS_ENABLE, comment="用户状态")
    deleted: M[bool] = mc(Boolean, default=False, comment="逻辑删除标志")


class UserAuth(ModelBase):
    __tablename__ = "t_user_auth"
    __table_args__ = (
        UniqueConstraint("user_id", "auth_type",
                         "auth_code", name="uni_user_auth"),
        {"comment": "用户认证信息"}
    )

    user_id: M[int] = mc(BigInteger, comment="用户ID")
    auth_type: M[int] = mc(
        Integer, default=UserSettings.AUTH_TYPE_PASSWORD, comment="认证类型")
    auth_code: M[str] = mc(
        String(128), default="", comment="认证类型code,如APPID等")
    auth_value: M[str] = mc(String(256), comment="认证值")
