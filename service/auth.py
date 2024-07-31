from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException
from api.config.security import client_aes_api, hash_api, jwt_api
from api.schema.auth import AuthAPI, PasswordLogin
from api.schema.errcode import APIErrors
from api.schema.base import Jwt
from api.model.user import UserStatus
from .base import get_session, Rsp


api = APIRouter(prefix="/auth")


@api.post("/password", summary="账号密码登录")
async def password_login(data: PasswordLogin, session=Depends(get_session)) -> Rsp:
    try:
        password = client_aes_api.decrypt(data.password_enc)

        user = AuthAPI.get_password_info(session, data.account)

        if user is None or hash_api.verify(password, user["auth_value"]) == False:
            return Rsp(**APIErrors.WRONG_ACCOUNT_PASSWD.value)

        if user["status"] != UserStatus.ENABLE:
            return Rsp(**APIErrors.ACCOUNT_STATUS_DISABLE.value)

        jwt = Jwt(user_uuid=user["user_uuid"])

        org = AuthAPI.get_user_orgs(session, user["user_id"])
        if org and len(org) == 1:
            jwt.org_uuid = org[0]["org_uuid"]

        payload = jwt_api.encode(**asdict(jwt))
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data={"jwt": payload})


# @api.post("/password")
# async def password_login(data: PasswordLogin, session=Depends(get_session)) -> Rsp:
#     """密码登录认证"""
#     try:
#         # 密码解密转换
#         password = client_aes_api.decrypt(data.password_enc)

#         # 获取账号信息
#         user_info = AuthAPI.get_account_info(session, data.account)

#         # 用户账号以及密码正确校验
#         if user_info is None or not hash_api.verify(password, user_info["auth_value"]):
#             return Rsp(**APIErrors.WRONG_ACCOUNT_PASSWD.value)

#         # 用户是否处于有效状态
#         if user_info["status"] == UserStatus.DISABLE.value:
#             return Rsp(**APIErrors.ACCOUNT_STATUS_DISABLE.value)

#         # 用户认证通过,构建JWT
#         jwt = JWT(user_id=user_info["user_id"])

#         # 如果用户仅有一个组织,直接设定组织信息
#         org_lists = AuthAPI.get_user_orgs(session, user_info["user_id"])
#         if org_lists and len(org_lists) == 1:
#             jwt.org_id = org_lists[0]["org_id"]

#         payload = jwt_api.encode(**jwt.model_dump())

#     except Exception as e:
#         raise HTTPException(500, f"{e}")

#     return Rsp(data={"jwt": payload})


# @api.get("/org")
# async def get_user_orgs(actor=Depends(get_actor_info)) -> Rsp:
#     """获取用户所属的有效组织信息"""
#     try:
#         data = AuthAPI.get_user_orgs(actor.session, actor.user_id)
#     except Exception as e:
#         raise HTTPException(500, f"{e}")
#     return Rsp(data=data)


# @api.post("/org")
# async def set_user_org(data: SelectOrg, actor=Depends(get_actor_info)) -> Rsp:
#     """登录用户选择对应的组织"""
#     try:

#         user_id, org_id = actor.user_id, data.org_id

#         # 判断用户选中的组织是否为有效的组织
#         result = AuthAPI.set_user_org(
#             actor.session, user_id, org_id)

#         if result != APIErrors.NO_ERROR:
#             return Rsp(**result.value)

#         jwt = JWT(user_id=user_id, org_id=org_id)
#         payload = jwt_api.encode(**jwt.model_dump())
#     except Exception as e:
#         raise HTTPException(500, f"{e}")

#     return Rsp(data={"jwt": payload})
