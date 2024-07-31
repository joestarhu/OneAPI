from typing import Any, Generator
from pydantic import BaseModel
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.config.settings import settings
from api.config.security import jwt_api
from api.schema.base import Pagination, Actor


engine = create_engine(
    settings.db_rds, echo=False, pool_recycle=settings.pool_recycle_seconds)
LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Rsp(BaseModel):
    code: int = 0
    message: str = "Succeed"
    data: Any | None = None


def get_pagination(page_idx: int = Query(default=1, description="页数"),
                   page_size: int = Query(default=10, description="每页数量")
                   ) -> Pagination:
    return Pagination(page_idx=page_idx, page_size=page_size)


def get_session() -> Generator:
    """数据库会话"""
    with LocalSession() as session:
        yield session


auth_bear = OAuth2PasswordBearer("/dummyUrl")


def get_actor_info(token=Depends(auth_bear), session=Depends(get_session)) -> Actor:
    jwt = jwt_api.decode(token)

    return Actor(user_id=jwt["user_id"], org_id=jwt["org_id"], session=session)