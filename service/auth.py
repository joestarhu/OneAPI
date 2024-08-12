from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException
from api.config.security import client_aes_api, hash_api, jwt_api
from api.schema.auth import AuthAPI, PasswordLogin, ChooseOrg
from api.schema.errcode import APIErrors
from api.schema.base import Jwt, Actor
from api.model.user import UserStatus
from .base import get_session, get_login_user, get_actor_info, Rsp

api = APIRouter(prefix="/auth")


@api.post("/password", summary="账号密码登录")
async def password_login(data: PasswordLogin, session=Depends(get_session)) -> Rsp:
    try:
        # 解密入参密码
        password = client_aes_api.decrypt(data.password_enc)

        # 获取用户认证信息(密码)
        user = AuthAPI.get_password_info(session, data.account)

        # 判断用户是否存在已经校验账密是否一致
        if user is None or hash_api.verify(password, user["auth_value"]) == False:
            return Rsp(**APIErrors.LOGIN_WRONG_ACCOUNT_PASSWD.value)

        # 用户状态是否有效
        if user["status"] != UserStatus.ENABLE.value:
            return Rsp(**APIErrors.LOGIN_ACCOUNT_STATUS_DISABLE.value)

        # 获取用户组织信息
        org = AuthAPI.get_user_orgs(
            Actor(session=session, user_uuid=user["user_uuid"]))

        # 构建JWT
        jwt = Jwt(user_uuid=user["user_uuid"])

        # 如果用户仅属于一个组织,则直接赋予登录组织相关信息
        if org and len(org) == 1:
            jwt.org_uuid = org[0]["org_uuid"]
            jwt.org_is_admin = org[0]["is_admin"] == True
            jwt.org_owner = org[0]["owner_uuid"] == user["user_uuid"]

        payload = jwt_api.encode(**asdict(jwt))
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data={"jwt": payload})


@api.get("/org_user", summary="获取已登录用户的信息")
async def get_org_user_info(actor=Depends(get_actor_info)) -> Rsp:
    try:
        data = AuthAPI.get_org_user_info(actor)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get("/org", summary="获取已登录用户的所属组织信息")
async def get_user_orgs(actor=Depends(get_login_user)) -> Rsp:
    try:
        data = AuthAPI.get_user_orgs(actor)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get("/org_name", summary="获取已登录的组织名称")
async def get_org_name(actor=Depends(get_actor_info)) -> Rsp:
    try:
        data = AuthAPI.get_login_org_name(actor)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)


@api.post("/org", summary="已登录用户选择登录组织")
async def set_user_org(data: ChooseOrg, actor=Depends(get_login_user)) -> Rsp:
    try:
        # 判断用户即将登录的组织是否有效
        org = AuthAPI.get_user_org(actor, data.org_uuid)

        if org is None:
            return Rsp(**APIErrors.LOGIN_ORG_DINED.value)

        # 更新JWT
        jwt = Jwt(user_uuid=actor.user_uuid,
                  org_uuid=data.org_uuid,
                  org_is_admin=org["is_admin"],
                  org_owner=org["owner_uuid"] == actor.user_uuid
                  )

        payload = jwt_api.encode(**asdict(jwt))
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data={"jwt": payload})
