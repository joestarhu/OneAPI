from enum import Enum
from sqlalchemy import SmallInteger, String, Boolean, BigInteger, UniqueConstraint
from .base import ModelBase, M, mc


class DataScopeDept(Enum):
    # 本人
    LOCAL = 0
    # 所有
    ALL = 99


class DataScopeRegion(Enum):
    # 本人
    LOCAL = 0
    # 所有
    ALL = 99


class AppStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class App(ModelBase):
    __tablename__ = "t_app"
    __table_args__ = (
        {"comment": "应用信息"}
    )

    app_name: M[str] = mc(String(64),
                          unique=True,
                          default="",
                          comment="应用名称"
                          )

    app_remark: M[str] = mc(String(256),
                            default="",
                            comment="应用备注"
                            )

    app_status: M[int] = mc(SmallInteger,
                            default=AppStatus.ENABLE.value,
                            comment="应用状态"
                            )

    is_deleted: M[bool] = mc(Boolean,
                             default=False,
                             comment="逻辑删除标识"
                             )


class AppService(ModelBase):
    __tablename__ = "t_app_service"
    __table__args__ = (
        UniqueConstraint("app_id", "service_tag",
                         name="uni_app_service"),
        {"comment": "应用鉴权服务"}
    )

    app_id: M[int] = mc(BigInteger,
                        default=0,
                        comment="应用ID"
                        )

    service_name: M[str] = mc(String(64),
                              default="",
                              comment="应用服务名称"
                              )

    service_tag: M[str] = mc(String(128),
                             default="",
                             comment="应用服务标识"
                             )


class AppRole(ModelBase):
    __tablename__ = "t_app_role"
    __table__args__ = (
        {"comment": "应用角色信息"}
    )

    app_id: M[int] = mc(BigInteger,
                        default=0,
                        comment="应用ID"
                        )

    role_id: M[int] = mc(BigInteger,
                         default=0,
                         comment="角色ID"
                         )

    org_uuid: M[str] = mc(String(32),
                          default="",
                          comment="角色所属组织"
                          )

    app_service_id: M[int] = mc(BigInteger,
                                default=0,
                                comment="应用鉴权服务ID"
                                )

    data_scope_dept: M[int] = mc(SmallInteger,
                                 default=DataScopeDept.LOCAL.value,
                                 comment="部门数据权限"
                                 )

    data_scope_region: M[int] = mc(SmallInteger,
                                   default=DataScopeRegion.LOCAL.value,
                                   comment="地区数据权限"
                                   )
