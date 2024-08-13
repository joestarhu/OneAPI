from enum import Enum
from sqlalchemy import SmallInteger, String, Boolean, BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped as M, mapped_column as mc
from .base import ModelBase


class AppUriType(Enum):
    # 内部路由
    ROUTER = 0
    # 外部链接
    HREF = 1


class AppServiceType(Enum):
    # 按钮级
    BUTTON = 0
    # 菜单级
    MENU = 1


class AppStatus(Enum):
    DISABLE = 0
    ENABLE = 1


class App(ModelBase):
    __tablename__ = "t_app"
    __table_args__ = (
        {"comment": "应用信息"}
    )

    name: M[str] = mc(String(32), comment="应用名")
    status: M[bool] = mc(Boolean, default=True, comment="应用状态")
    desc: M[str] = mc(String(128), default="", comment="应用描述")
    icon: M[str] = mc(String(128), default="", comment="应用icon")
    uri_type: M[int] = mc(
        SmallInteger, default=AppUriType.ROUTER.value, comment="应用链接类型")
    uri_value: M[str] = mc(String(128), default="", comment="应用链接URI")


class AppService:
    __tablename__ = "t_app_service"
    __table_args__ = (
        UniqueConstraint("app_id", "service_name", name="uni_app_service"),
        {"comment": "应用服务信息"}
    )

    app_id: M[int] = mc(BigInteger, comment="应用ID")
    service_type: M[int] = mc(
        SmallInteger, default=AppServiceType.BUTTON.value, comment="服务类型")
    service_name: M[str] = mc(String(64), default="", comment="服务名称")
