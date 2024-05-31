from fastapi import APIRouter, Depends, Query
from api.api.base import get_page, user_auth
from api.service.account import AccountAPI, AccountList, AccountCreate  # noqa

api = APIRouter(prefix="/account")


@api.get("/list", summary="获取账户信息列表")
def get_list(*, actor=Depends(user_auth), page=Depends(get_page),
             nick_name: str = Query(default=None, description="用户昵称"),
             phone: str = Query(default=None, description="手机号"),
             status: int = Query(default=None, description="账户状态")
             ):
    data = AccountList(**page, nick_name=nick_name, phone=phone, status=status)
    return AccountAPI.get_list(actor.db, data)


@api.get("/detail", summary="获取账户详情")
def get_detail(*, actor=Depends(user_auth), user_id: int = Query(description="账户ID")):
    return AccountAPI.get_detail(actor.db, user_id)


@ api.post("/create", summary="创建账户")
def account_create(*, actor=Depends(user_auth), data: AccountCreate):
    return AccountAPI.create_account(actor.db, actor.act, data)


@api.post("/update", summary="修改账户")
def account_update(*, actor=Depends(user_auth)):
    return {}


@api.post("/delete", summary="删除账户")
def account_delete(*, actor=Depends(user_auth)):
    return {}
