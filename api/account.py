from fastapi import APIRouter, Depends, Query
from api.api.base import get_db, get_page
from api.service.account import AccountAPI, AccountList  # noqa

api = APIRouter(prefix="/account")


@api.get("/list", summary="获取账户信息列表")
def get_list(*, db=Depends(get_db), page=Depends(get_page),
             nick_name: str = Query(default=None, description="用户昵称"),
             phone: str = Query(default=None, description="手机号"),
             status: int = Query(default=None, description="账户状态")
             ):
    data = AccountList(**page, nick_name=nick_name, phone=phone, status=status)
    return AccountAPI.get_list(db, data)
