from fastapi import APIRouter, Depends, Query
from api.api.base import get_db, get_page, get_user_id  # noqa
from api.service.auth import AuthAPI, PasswordLogin, SelectedOrg  # noqa


api = APIRouter(prefix="/auth")


@api.get("/org", summary="获取用户所属组织")
def get_user_orgs(*, db=Depends(get_db), user_id=Depends(get_user_id)):
    return AuthAPI.get_user_orgs(db, user_id)


@api.get("/userinfo", summary="获取登录用户信息")
def get_login_info():
    ...


@api.post("/password", summary="密码登录")
def password_login(*, db=Depends(get_db), data: PasswordLogin):
    return AuthAPI.password_login(db, data)


@api.post("/org", summary="选择登录组织")
def select_org(*, db=Depends(get_db), user_id=Depends(get_user_id), data: SelectedOrg):
    return AuthAPI.set_user_org(db, user_id, data)
