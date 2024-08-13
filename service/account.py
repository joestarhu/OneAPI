from fastapi import APIRouter, Depends, HTTPException, Query, Security
from pydantic import BaseModel, Field
from api.model.user import User, UserAuth
from api.schema.account import AccountAPI, AccountCreate, AccountUpdate, AccountDelete

from .base import get_actor_info, get_pagination, Rsp

api = APIRouter(prefix="/account")


@api.get("/list", summary="获取账号列表信息")
async def get_list(phone: str = Query(default="", description="手机号"),
                   nick_name: str = Query(default="", description="用户昵称"),
                   status: int = Query(default=None, description="用户状态"),
                   pagination=Depends(get_pagination),
                   actor=Security(get_actor_info, scopes=["acct:list"])
                   ) -> Rsp:
    try:
        data = AccountAPI.get_account_list(
            actor, pagination, phone, nick_name, status)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)


@api.get("/detail", summary="获取账号详细信息")
async def get_detail(user_uuid: str = Query(description="用户UUID"),
                     actor=Security(get_actor_info, scopes=["acct:detail"])
                     ) -> Rsp:
    try:
        data = AccountAPI.get_account_detail(actor, user_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.post("/create", summary="创建账号")
async def create(data: AccountCreate,
                 actor=Security(get_actor_info, scopes=["acct:create"])
                 ) -> Rsp:
    """创建账号"""
    try:
        result = AccountAPI.create_account(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)


@api.post("/update", summary="修改账号")
async def update(data: AccountUpdate,
                 actor=Security(get_actor_info, scopes=["acct:update"])
                 ) -> Rsp:
    """更新账号"""
    try:
        result = AccountAPI.update_account(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)


@api.post("/delete", summary="删除账号")
async def delete(data: AccountDelete,
                 actor=Security(get_actor_info, scopes=["acct:delete"])
                 ) -> Rsp:
    """更新账号"""
    try:
        result = AccountAPI.delete_account(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)
