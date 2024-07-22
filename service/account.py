from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, and_
from jhu.orm import ORM, ORMFormatRule
from api.model.user import User, UserAuth, UserSettings, UserAPI
from api.config.security import FieldSecurity
from api.config.settings import settings
from .deps import get_page, get_actor, Rsp, http_wrapper

api = APIRouter(prefix="/account")


format_rules = [ORMFormatRule("phone", FieldSecurity.phone_decrypt)]


class AccountCreate(BaseModel):
    account: str
    nick_name: str
    phone: str
    status: int


class AccountUpdate(BaseModel):
    user_id: int
    nick_name: str
    status: int


class AccountDelete(BaseModel):
    user_id: int


@api.get("/list")
async def get_account_list(phone: str = "", nick_name: str = "", status: int = None, page=Depends(get_page), act=Depends(get_actor)) -> Rsp:
    # 查询条件构造
    expressions = [expression for condition, expression in [
        (phone, User.phone.contains(FieldSecurity.phone_encrypt(phone))),
        (nick_name, User.nick_name.contains(nick_name)),
        (status is not None, User.status == status)
    ] if condition]

    stmt = select(
        User.id,
        User.account,
        User.nick_name,
        User.phone,
        User.status,
        User.create_dt,
        User.update_dt
    ).where(
        and_(User.deleted == False, *expressions)
    )
    # 分页查询处理
    try:
        data = ORM.pagination(act.db, stmt,
                              page_idx=page["page_idx"],
                              page_size=page["page_size"],
                              order=[User.create_dt.desc()],
                              format_rules=format_rules)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return Rsp(data=data)


@api.get("/detail")
async def get_account_detail(user_id: int, act=Depends(get_actor)) -> Rsp:

    stmt = select(
        User.id,
        User.account,
        User.phone,
        User.nick_name,
        User.status
    ).where(
        and_(User.deleted == False, User.id == user_id)
    )

    data = ORM.one(act.db, stmt, format_rules)

    return Rsp(data=data)


@api.post("/create")
async def create_account(data: AccountCreate, act=Depends(get_actor)) -> Rsp:
    user = User(**data.model_dump(), **act.db_create)
    user_auth = UserAuth(auth_type=UserSettings.AUTH_TYPE_PASSWORD,
                         auth_identify="", auth_value=settings.default_passwd, **act.db_create)

    try:
        err_info = UserAPI.create(act.db, user, user_auth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return Rsp(**err_info.value)


@api.post("/update")
async def update_account(data: AccountUpdate, act=Depends(get_actor)) -> Rsp:
    try:
        user = User(id=data.user_id, nick_name=data.nick_name,
                    status=data.status, **act.db_update)
        err_info = UserAPI.update(act.db, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return Rsp(**err_info.value)


@api.post("/delete")
async def delete_account(data: AccountDelete, act=Depends(get_actor)) -> Rsp:
    try:
        user = User(id=data.user_id, **act.db_update)
        err_info = UserAPI.delete(act.db, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return Rsp(**err_info.value)
