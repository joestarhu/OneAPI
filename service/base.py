from datetime import datetime
from typing import Any, Dict
from math import ceil
from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select, Select, MappingResult
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import BinaryExpression


class ActInfo(BaseModel):
    """操作信息
    """
    user_id: int = Field(description="用户ID")
    org_id: int | None = Field(default=None, description="登录组织ID")
    url_path: str = Field(default="", description="请求路由标识")
    # act_datetime:datetime = Field(default=datetime.now(ZoneInfo("UTC")),description="操作数据时间")

    @property
    def insert_info(self) -> dict:
        user_id = self.user_id
        act_datetime = datetime.now()

        return dict(
            create_id=user_id, update_id=user_id,
            create_dt=act_datetime, update_dt=act_datetime,
        )

    @property
    def update_info(self) -> dict:
        return dict(update_id=self.user_id, update_dt=datetime.now())


class Rsp(BaseModel):
    """请求成功返回信息
    """
    code: int = Field(default=0, description="请求结果代码;0表示成功")
    message: str = Field(default="成功", description="请求结果消息描述")
    data: Any = None


class RspError(HTTPException):
    """请求失败返回信息
    """

    def __init__(self, code: int = 500, message: str = "服务器内部错误,请重试或联系管理员", data: Any = None, headers: Dict[str, str] | None = None) -> None:
        rsp = Rsp(code=code, message=message, data=data)
        super().__init__(code, rsp.model_dump(), headers)


class Pagination(BaseModel):
    """分页请求参数
    """
    page_idx: int = Field(default=1, description="页数ID")
    page_size: int = Field(default=10, description="每页数量")


def format_datetime(dt: datetime) -> str:
    """格式化日期
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_dict(data: dict, rules: list = []) -> dict:
    """对数据库的返回结果进行标准统一的格式化
    """
    base_rules = [
        ("create_dt", format_datetime),
        ("update_dt", format_datetime),
    ]
    base_rules.extend(rules)

    for kw, func in base_rules:
        if data.get(kw, None) is not None:
            data[kw] = func(data[kw])
    return data


def orm_wrapper(func):
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except RspError as e:
            raise e
        except Exception as e:
            raise RspError(data=f"{e}")
    return wrapper


class ORM:
    @staticmethod
    def commit(db: Session, stmt):
        """事务提交
        """
        try:
            db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f"{e}")

    @orm_wrapper
    @staticmethod
    def unique_chk(db: Session, rules: list, expression: BinaryExpression = None) -> Rsp | None:
        """数据库数据唯一性检测

        Args:
            db: 数据库会话
            rules: 检测规则
            expression: 表达式

        Return:
            None:正常,无重复数据
            Rsp:异常,存在重复数据
        """
        base_stmt = select(1)

        if expression is not None:
            base_stmt = base_stmt.where(expression)

        for errmsg, condition in rules:
            stmt = base_stmt.where(condition)
            if ORM.counts(db, stmt) > 0:
                return Rsp(code=1, message=errmsg)

    @staticmethod
    def mapping(db: Session, stmt) -> MappingResult:
        """ORM执行结果mapping
        """
        return db.execute(stmt).mappings()

    @orm_wrapper
    @staticmethod
    def all(db: Session, stmt: Select, fmt_rules: list = []) -> list[dict]:
        """获取所有数据
        """
        ds = ORM.mapping(db, stmt)
        result = []
        for one in ds:
            data = format_dict(dict(**one), fmt_rules)
            result.append(data)
        return result

    @orm_wrapper
    @staticmethod
    def one(db: Session, stmt: Select, fmt_rules: list = []) -> dict | None:
        """获取第一行数据
        """
        try:
            one = next(ORM.mapping(db, stmt))
            data = format_dict(dict(**one), fmt_rules)
            return data
        except StopIteration:
            return None

    @orm_wrapper
    @staticmethod
    def counts(db: Session, stmt: Select) -> int:
        """获取数据量
        """
        return db.scalar(stmt.with_only_columns(func.count("1")))

    @orm_wrapper
    @staticmethod
    def pagination(db: Session, stmt=Select, page_idx: int = 1, page_size: int = 10, order: list = None, fmt_rules: list = []) -> dict:
        """分页查询数据
        """
        page_size = 1 if page_size < 1 else page_size

        match(page_idx):
            case page_idx if page_idx > 0:
                offset = (page_idx - 1) * page_size
            case _:
                offset = 0
                page_idx = 1

        total = ORM.counts(db, stmt)
        page_total = ceil(total / page_size)

        if order:
            stmt = stmt.order_by(*order)
        stmt = stmt.offset(offset).limit(page_size)
        records = ORM.all(db, stmt, fmt_rules)

        pagination = dict(page_idx=page_idx, page_size=page_size,
                          page_total=page_total, total=total)

        return dict(records=records, pagination=pagination)
