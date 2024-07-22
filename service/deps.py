from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Generator, TypeVar
from fastapi import Query, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from api.config.settings import settings
from api.config.security import jwt_api

engine = create_engine(url=settings.db_rds, echo=False,
                       pool_recycle=settings.pool_recycle_seconds)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 获取相关用户信息
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/dummy/login")


T_RSPDATA = TypeVar("T_RSPDATA", dict, list, None)


class Rsp(BaseModel):
    """请求成功返回信息
    """
    code: int = Field(default=0, description="请求结果代码;0表示成功")
    message: str = Field(default="Succeed", description="请求结果消息描述")
    data: T_RSPDATA = None


@dataclass
class JWT:
    user_id: int
    org_id: int


@dataclass
class ActInfo:
    db: Session = None
    user_id: int = None

    @property
    def db_create(self) -> dict:
        dt = datetime.now()
        return dict(create_id=self.user_id, update_id=self.user_id, create_dt=dt, update_dt=dt)

    @property
    def db_update(self) -> dict:
        dt = datetime.now()
        return dict(update_id=self.user_id, update_dt=dt)


def http_wrapper(func):
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")
    return wrapper


def get_db() -> Generator:
    """获取数据库会话"""
    with SessionLocal() as db:
        yield db


def get_actor(db=Depends(get_db), jwt=Depends(oauth2_schema)) -> ActInfo:
    act = ActInfo(db=db)
    try:
        jwt_dict = jwt_api.decode(jwt)
        act.user_id = jwt_dict["user_id"]
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"{e}")
    return act


def get_page(page_idx: int = Query(default=1, description="页数"), page_size: int = Query(default=10, description="每页数量")) -> dict:
    """获取默认请求分页数据"""
    return dict(page_idx=page_idx, page_size=page_size)
