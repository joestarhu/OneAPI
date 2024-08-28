from dataclasses import dataclass, asdict
from fastapi import APIRouter, Depends, HTTPException
from api.config.security import client_aes_api, hash_api, jwt_api
from api.model.user import UserStatus
from api.model.org import OrgUserStatus
from api.schema.auth import AuthAPI, PasswordLogin
from api.schema.errcode import APIErrors
from .base import Rsp, get_session, get_login_user, get_actor_info


@dataclass
class Jwt:
    """jwt相关信息"""
    # 用户uuid
    user_uuid: str
    # 组织uuid
    org_uuid: str | None = None
    # 是否组织所有有者(默认False)
    org_owner: bool = False

    # 是否管理者组织(默认False)
    org_is_admin: bool = False

    # 权限范围
    scopes: list[str] | None = None


api = APIRouter(prefix="/auth")


@api.post("/password", summary="账号密码登录")
async def password_login(data: PasswordLogin,
                         session=Depends(get_session)
                         ) -> Rsp:
    try:
        # 客户端密码解密
        password = client_aes_api.decrypt(data.password_enc)

        # 取默认的密码信息
        user = AuthAPI.get_account_auth_info(session, data.account)

        # 用户是否存在以及账密是否一致
        if user is None or hash_api.verify(password, user["auth_value"]) == False:
            return Rsp(**APIErrors.LOGIN_WRONG_ACCOUNT_PASSWD.value)

        # 用户密码认证通过后再判断登录状态是否有效
        if user["status"] != UserStatus.ENABLE.value:
            return Rsp(**APIErrors.LOGIN_ACCOUNT_STATUS_DISABLE.value)

        # 构建用户jwt
        jwt = Jwt(user_uuid=user["user_uuid"])

        # 获取用户的有效可登录的组织信息
        org_list = AuthAPI.get_user_org_list(session, user["user_uuid"])

        if org_list and len(org_list) == 1 and org_list[0]["org_user_status"] == OrgUserStatus.ENABLE.value:
            jwt.org_uuid = org_list[0]["org_uuid"]
            jwt.org_owner = user["user_uuid"] == org_list[0]["owner_uuid"]

        payload = jwt_api.encode(**asdict(jwt))
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data={"jwt": payload})


@api.post("/choose_org", summary="选择登录的组织")
async def choose_org() -> Rsp:
    try:
        NotImplementedError
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp()


@api.get("/org", summary="获取已登录用户所属的组织信息")
async def get_user_orgs(actor=Depends(get_login_user)) -> Rsp:
    try:
        NotImplementedError
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp()


@api.get("/org_user", summary="获取已登录组织用户的信息")
async def get_org_user_info(actor=Depends(get_actor_info)) -> Rsp:
    try:
        data = AuthAPI.get_org_user_info(actor)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)


@api.get("/org_name", summary="获取已登录组织的名称")
async def get_org_name(actor=Depends(get_actor_info)) -> Rsp:
    try:
        data = AuthAPI.get_org_name(actor)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)

    # @api.get("/org", summary="获取已登录用户的所属组织信息")
    # async def get_user_orgs(actor=Depends(get_login_user)) -> Rsp:
    #     try:
    #         data = AuthAPI.get_user_orgs(actor)
    #     except Exception as e:
    #         raise HTTPException(500, f"{e}")
    #     return Rsp(data=data)

    # @api.get("/org_name", summary="获取已登录的组织名称")
    # async def get_org_name(actor=Depends(get_actor_info)) -> Rsp:
    #     try:
    #         data = AuthAPI.get_login_org_name(actor)
    #     except Exception as e:
    #         raise HTTPException(500, f"{e}")

    #     return Rsp(data=data)

    # @api.post("/org", summary="已登录用户选择登录组织")
    # async def set_user_org(data: ChooseOrg, actor=Depends(get_login_user)) -> Rsp:
    #     try:
    #         # 判断用户即将登录的组织是否有效
    #         org = AuthAPI.get_user_org(actor, data.org_uuid)

    #         if org is None:
    #             return Rsp(**APIErrors.LOGIN_ORG_DINED.value)

    #         # 更新JWT
    #         jwt = Jwt(user_uuid=actor.user_uuid,
    #                   org_uuid=data.org_uuid,
    #                   org_is_admin=org["is_admin"],
    #                   org_owner=org["owner_uuid"] == actor.user_uuid
    #                   )

    #         payload = jwt_api.encode(**asdict(jwt))
    #     except Exception as e:
    #         raise HTTPException(500, f"{e}")

    #     return Rsp(data={"jwt": payload})
