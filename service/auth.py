from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from api.config.errcode import ErrCode
from api.config.security import hash_api, client_aes_api, jwt_api
from api.model.user import UserSettings, UserAPI
from .deps import get_db, JWT, Rsp


api = APIRouter(prefix="/auth")


class PasswrodLogin(BaseModel):
    account: str = Field(description="用户账号")
    password_enc: str = Field(description="密码(hash)加密")


@api.post("/password", summary="密码登录")
async def passwd_login(*, db=Depends(get_db), data: PasswrodLogin):
    try:
        # 解密用户的密码
        passwd = client_aes_api.decrypt(data.password_enc)

        # 获取账号信息
        user_info = UserAPI.get_user_auth_info(
            db, auth_type=UserSettings.AUTH_TYPE_PASSWORD, auth_identify="", account=data.account)

        # 判断账号是否存在,以及密码是否有效
        if user_info is None or not hash_api.verify(passwd, user_info["auth_value"]):
            return Rsp(**ErrCode.WRONG_ACCOUNT_PASSWD.value)

        # 判断账号状态是否有效
        if user_info["status"] == UserSettings.STATUS_DISABLE:
            return Rsp(**ErrCode.STATUS_DISBALE.value)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    # 构建JWT信息
    jwt = JWT(user_id=user_info["id"], org_id=1)

    data = jwt_api.encode(**asdict(jwt))
    return Rsp(data={"jwt": data})
