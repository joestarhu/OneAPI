from typing import Generator
from dataclasses import dataclass
from fastapi import Query, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm.session import Session


from api.model.base import SessionLocal  # noqa
from api.service.base import ActInfo  # noqa
from api.service.auth import AuthAPI  # noqa


@dataclass
class Actor:
    db: Session
    act: ActInfo | None = None


def get_db() -> Generator:
    """获取关系型数据库会话
    """
    with SessionLocal() as session:
        yield session


def get_page(page_idx: int = Query(default=1, description="页数"), page_size: int = Query(default=10, description="每页数量")) -> dict:
    """获取默认请求分页数据
    """
    return dict(page_idx=page_idx, page_size=page_size)


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/dummy/login")


def user_auth(*, db=Depends(get_db), token=Depends(oauth2_schema), req: Request) -> Actor:
    """从JWT中获取用户信息,并鉴权是否具备权限
    """
    actor = Actor(db=db)
    payload = AuthAPI.jwt_decode(token)
    user = payload["user"]
    # permission = payload.get("permission",None)

    # if permission is not None and (permission["admin"] or req.url.path in permission["fn"]):
    #     pass
    # else:
    #     raise RspError(code=403,message="无权限")

    # act = ActInfo(user_id = user["user_id"],org_id=payload["login_org"])
    actor.act = ActInfo(user_id=user["user_id"])
    return actor
