from typing import Generator, Any
from pydantic import BaseModel
from fastapi import HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.config.settings import settings
from api.config.security import jwt_api
from api.schema.base import Pagination, Actor


engine = create_engine(settings.db_rds,
                       echo=False, pool_recycle=settings.pool_recycle_seconds)
local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Rsp(BaseModel):
    """Restful API Response"""
    code: int = 0
    message: str = "Succeed"
    data: Any | None = None


def get_session() -> Generator:
    """获取数据库会话"""
    with local_session() as session:
        yield session


def get_pagination(page_idx: int = Query(default=1, description="页数"),
                   page_size: int = Query(default=10, description="每页数量")
                   ) -> Pagination:
    return Pagination(page_idx=page_idx, page_size=page_size)


auth_bear = OAuth2PasswordBearer("/auth/docs_login")


def get_login_user(token=Depends(auth_bear),
                   session=Depends(get_session)
                   ) -> Actor:
    """获取操作者信息"""
    try:
        jwt = jwt_api.decode(token)
        user_uuid = jwt["user_uuid"]
        org_uuid = jwt["org_uuid"]
        org_owner = jwt["org_owner"]
        scopes = jwt["scopes"]

    except Exception as e:
        raise HTTPException(401, f"{e}")

    return Actor(session=session, user_uuid=user_uuid, org_uuid=org_uuid, is_org_owner=org_owner)


def get_actor_info(security_scope: SecurityScopes,
                   actor=Depends(get_login_user)
                   ) -> Actor:
    try:

        # 组织所有者无需鉴权
        if actor.is_org_owner:
            return actor

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return actor


# def get_actor_info(security_scopes: SecurityScopes, actor=Depends(get_login_user)) -> Actor:
#     try:
#         # 用户状态需要保障是有效的
#         if AuthAPI.check_login_avaiable(actor.session, actor.user_uuid, actor.org_uuid) == False:
#             raise HTTPException(401, "无效的用户或组织")

#         # 如果是超级管理员则无需鉴权
#         if actor.org_owner:
#             return actor

#         # 如请求接口带鉴权标识,则进行权限判断
#         if security_scopes.scopes and (scope := security_scopes.scopes[0]):
#             if actor.scopes is None or scope not in actor.scopes:
#                 raise HTTPException(403, "Access Dined")
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(500, f"{e}")

#     return actor
