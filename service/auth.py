from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.orm.session import Session
from api.config.security import FieldSecurity, client_aes_api, hash_api, jwt_api  # noqa
from api.model.user import User, UserAuth, UserSettings  # noqa
from api.service.base import ORM, Rsp, RspError, Pagination  # noqa


class AuthErrCode:
    # 账户被停用
    ERR_ACCOUNT_STATUS_DISABLE: int = 1000
    # 账户或密码错误
    ERR_PASSWORD_LOGIN: int = 1001


class JwtUser(BaseModel):
    user_id: int
    nick_name: str


class JwtPayload(BaseModel):
    user: JwtUser
    # org: JwtOrg | None = None


class PasswordLogin(BaseModel):
    """账密登录
    """
    account: str = Field(description="账号")
    password_enc: str = Field(description="密码(加密)")


class AuthAPI:
    @staticmethod
    def jwt_encode(user: JwtUser) -> str:
        """jwt构建
        """
        payload = JwtPayload(user=user).model_dump()
        return jwt_api.encode(**payload)

    @staticmethod
    def jwt_decode(token: str) -> dict:
        """jwt解构
        """
        try:
            jwt_data = jwt_api.decode(token)

            payload = {}
            for kw in JwtPayload.model_fields.keys():
                payload[kw] = jwt_data.get(kw, None)
        except Exception as e:
            raise RspError(401, "无效的用户token", f"{e}")

        return payload

    @staticmethod
    def password_login(db: Session, data: PasswordLogin) -> Rsp:
        """密码登录
        """
        # 前端密码解密
        try:
            password = client_aes_api.decrypt(data.password_enc)
        except Exception as e:
            raise RspError(code=400, data=f"{e}")

        # 查询账号的基本信息
        stmt = select(
            User.id,
            User.nick_name,
            User.status,
            UserAuth.auth_value
        ).join_from(
            User, UserAuth, User.id == UserAuth.user_id
        ).where(
            and_(
                User.deleted == False,
                User.account == data.account,
                UserAuth.auth_type == UserSettings.AUTH_TYPE_PASSWORD,
                UserAuth.auth_code == ""
            )
        )

        info = ORM.one(db, stmt)

        if info is None or hash_api.verify(password, info["auth_value"]) == False:
            return Rsp(code=AuthErrCode.ERR_PASSWORD_LOGIN, message="抱歉,您的账号或密码错误")

        if info["status"] == UserSettings.STATUS_DISABLE:
            return Rsp(code=AuthErrCode.ERR_ACCOUNT_STATUS_DISABLE, message="抱歉,您的账号已被停用")

        jwt_user = JwtUser(user_id=info["id"], nick_name=info["nick_name"])

        return Rsp(data=AuthAPI.jwt_encode(jwt_user))
