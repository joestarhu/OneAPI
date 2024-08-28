from enum import Enum
from sqlalchemy import String, SmallInteger, BigInteger, Boolean
from .base import ModelBase, M, mc


class RoleStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class Role(ModelBase):
    __tablename__ = "t_role"
    __table_args__ = (
        {"comment": "角色信息"}
    )

    role_name: M[str] = mc(String(64),
                           unique=True,
                           default="",
                           comment="角色名"
                           )
    org_uuid: M[str] = mc(String(32),
                          default="",
                          comment="角色所属组织,空表示默认角色,可在所有组织下使用"
                          )

    role_remark: M[str] = mc(String(256),
                             default="",
                             comment="角色备注"
                             )

    role_status: M[int] = mc(SmallInteger,
                             default=RoleStatus.ENABLE.value,
                             comment="角色状态"
                             )

    is_deleted: M[bool] = mc(Boolean,
                             default=False,
                             comment="逻辑删除标识"
                             )
