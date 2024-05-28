from fastapi import APIRouter, Depends, Query

from api.api.base import get_db, get_page  # noqa
from api.service.auth import AuthAPI, PasswordLogin  # noqa


api = APIRouter(prefix="/auth")


@api.post("/password", summary="密码登录")
def password_login(*, db=Depends(get_db), data: PasswordLogin):
    return AuthAPI.password_login(db, data)
