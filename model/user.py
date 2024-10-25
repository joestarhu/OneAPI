from enum import Enum
from sqlalchemy import String, SmallInteger, Boolean, UniqueConstraint
from .base import ModelBase, M, mc


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

    user_uuid: M[str] = mc(String(32),
                           unique=True,
                           default="",
                           comment="用户UUID"
                           )

    account: M[str] = mc(String(64),
                         unique=True,
                         default="",
                         comment="用户账号"
                         )

    nick_name: M[str] = mc(String(64),
                           default="",
                           comment="用户昵称"
                           )

    phone_enc: M[str] = mc(String(256),
                           default="",
                           comment="用户手机号(加密)"
                           )

    avatar_url: M[str] = mc(String(256),
                            default="",
                            comment="用户头像url"
                            )

    user_status: M[int] = mc(SmallInteger,
                             default=UserStatus.ENABLE.value,
                             comment="用户状态;0:停用,1:启用"
                             )

    is_deleted: M[bool] = mc(Boolean,
                             default=False,
                             comment="逻辑删除标识"
                             )


class UserAuth(ModelBase):
    __tablename__ = "t_user_auth"
    __table_args__ = (
        UniqueConstraint("user_uuid", "auth_type", "auth_identify",
                         name="uni_user_auth"),
        {"comment": "用户认证信息"}
    )

    user_uuid: M[str] = mc(String(32),
                           default="",
                           comment="用户UUID"
                           )

    auth_type: M[int] = mc(SmallInteger,
                           default=UserAuthType.PASSWORD.value,
                           comment="认证类型"
                           )

    auth_identify: M[str] = mc(String(128),
                               default="",
                               comment="认证类型标识"
                               )

    auth_value: M[str] = mc(String(256),
                            default="",
                            comment="认证值"
                            )
