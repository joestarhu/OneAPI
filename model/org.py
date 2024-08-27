from enum import Enum
from sqlalchemy import Boolean, Integer, SmallInteger, String, UniqueConstraint
from .base import ModelBase, M, mc


class OrgStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class OrgUserStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class OrgAppStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class Org(ModelBase):
    __tablename__ = "t_org"
    __table_args__ = (
        {"comment": "组织信息"}
    )

    org_uuid: M[str] = mc(String(32),
                          unique=True,
                          default="",
                          comment="组织UUID"
                          )

    org_name: M[str] = mc(String(64),
                          unique=True,
                          default="",
                          comment="组织名称"
                          )

    owner_uuid: M[str] = mc(String(32),
                            default="",
                            comment="组织所有者UUID"
                            )

    remark: M[str] = mc(String(256),
                        default="",
                        comment="组织备注信息"
                        )

    status: M[int] = mc(SmallInteger,
                        default=OrgStatus.ENABLE.value,
                        comment="组织状态"
                        )

    is_deleted: M[bool] = mc(Boolean,
                             default=False,
                             comment="逻辑删除标识"
                             )


class OrgUser(ModelBase):
    __tablename__ = "t_org_user"
    __table_args__ = (
        UniqueConstraint("org_uuid", "user_uuid",
                         name="uni_org_user"),
        {"comment": "组织用户信息"}
    )

    org_uuid: M[str] = mc(String(32),
                          default="",
                          comment="组织UUID"
                          )

    user_uuid: M[str] = mc(String(32),
                           default="",
                           comment="用户UUID"
                           )

    org_user_name: M[str] = mc(String(64),
                               default="",
                               comment="用户在组织内的名称"
                               )

    org_user_avatar_url: M[str] = mc(String(256),
                                     default="",
                                     comment="用户在组织内的头像URL"
                                     )

    org_user_status: M[int] = mc(SmallInteger,
                                 default=OrgUserStatus.ENABLE.value,
                                 comment="用户在组织内的状态"
                                 )


# class OrgApp(ModelBase):
#     __tablename__ = "t_org_app"
#     __table_args__ = (
#         UniqueConstraint("org_uuid", "app_id", name="uni_org_user"),
#         {"comment": "组织应用信息"}
#     )

#     org_uuid: M[int] = mc(String(32), comment="组织UUID")

#     status: M[int] = mc(
#         Integer, default=OrgAppStatus.ENABLE.value, comment="组织应用状态")
