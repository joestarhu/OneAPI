from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from api.model.user import User, UserAuth
from api.schema.account import AccountAPI, AccountCreate, AccountUpdate, AccountDelete

from .base import get_actor_info, get_pagination, Rsp

api = APIRouter(prefix="/account")


@api.get("/list")
async def get_list(phone: str = Query(default="", description="手机号"),
                   nick_name: str = Query(default="", description="用户昵称"),
                   status: int = Query(default=None, description="用户状态"),
                   pagination=Depends(get_pagination),
                   actor=Depends(get_actor_info)
                   ) -> Rsp:
    try:
        data = AccountAPI.get_account_list(
            actor, pagination, phone, nick_name, status)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)


@api.get("/detail")
async def get_detail(user_uuid: str = Query(description="用户UUID"),
                     actor=Depends(get_actor_info)
                     ) -> Rsp:
    try:
        data = AccountAPI.get_account_detail(actor, user_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.post("/create")
async def create(data: AccountCreate,
                 actor=Depends(get_actor_info)
                 ) -> Rsp:
    """创建账号"""
    try:
        result = AccountAPI.create_account(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)


@api.post("/update")
async def update(data: AccountUpdate,
                 actor=Depends(get_actor_info)
                 ) -> Rsp:
    """更新账号"""
    try:
        result = AccountAPI.update_account(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)


@api.post("/delete")
async def delete(data: AccountDelete,
                 actor=Depends(get_actor_info)
                 ) -> Rsp:
    """更新账号"""
    try:
        result = AccountAPI.delete_account(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)
