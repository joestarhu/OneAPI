from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException
from api.config.security import client_aes_api, hash_api, jwt_api
from api.schema.auth import AuthAPI, PasswordLogin, SelectOrg
from api.schema.errcode import APIErrors
from api.schema.base import Jwt, Actor
from api.model.user import UserStatus
from .base import get_session, get_actor_info, Rsp


api = APIRouter(prefix="/auth")


@api.post("/password", summary="账号密码登录")
async def password_login(data: PasswordLogin,
                         session=Depends(get_session)
                         ) -> Rsp:
    try:
        password = client_aes_api.decrypt(data.password_enc)

        user = AuthAPI.get_password_info(session, data.account)

        if user is None or hash_api.verify(password, user["auth_value"]) == False:
            return Rsp(**APIErrors.WRONG_ACCOUNT_PASSWD.value)

        if user["status"] != UserStatus.ENABLE.value:
            return Rsp(**APIErrors.ACCOUNT_STATUS_DISABLE.value)

        jwt = Jwt(user_uuid=user["user_uuid"])

        org = AuthAPI.get_user_orgs(
            Actor(session=session, user_uuid=user["user_uuid"]))
        if org and len(org) == 1:
            jwt.org_uuid = org[0]["org_uuid"]
            jwt.org_is_admin = org[0]["is_admin"] == True
            jwt.org_owner = org[0]["owner_uuid"] == user["user_uuid"]

        payload = jwt_api.encode(**asdict(jwt))
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data={"jwt": payload})


@api.get("/org_user", summary="获取组织的用户信息")
async def get_org_user_info(actor=Depends(get_actor_info)
                            ) -> Rsp:
    try:
        data = AuthAPI.get_org_user_info(actor)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get("/org", summary="获取登录用户组织信息")
async def get_user_orgs(actor=Depends(get_actor_info)
                        ) -> Rsp:
    try:
        data = AuthAPI.get_user_orgs(actor)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.post("/org", summary="选择登录组织")
async def set_user_org(data: SelectOrg,
                       actor=Depends(get_actor_info)
                       ) -> Rsp:
    try:
        if (result := AuthAPI.check_user_org(actor, data.org_uuid)) != APIErrors.NO_ERROR:
            return Rsp(**result.value)

        # 更新JWT
        jwt = Jwt(user_uuid=actor.user_uuid, org_uuid=data.org_uuid)
        payload = jwt_api.encode(**asdict(jwt))
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data={"jwt": payload})
