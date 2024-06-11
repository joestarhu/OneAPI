from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.orm.session import Session
from api.config.security import FieldSecurity, client_aes_api, hash_api, jwt_api  # noqa
from api.model.user import User, UserAuth, UserSettings  # noqa
from api.model.org import Org, OrgUser, OrgSettings  # noqa
from api.service.base import ORM, Rsp, RspError, Pagination  # noqa


class AuthErrCode:
    # 账户被停用
    ERR_ACCOUNT_STATUS_DISABLE: int = 1000
    # 账户或密码错误
    ERR_PASSWORD_LOGIN: int = 1001


class JwtUser(BaseModel):
    # 用户ID
    user_id: int
    # 用户昵称
    nick_name: str


class JwtOrg(BaseModel):
    # 登录用户的组织ID
    org_id: int | None = None
    # 登录用户的组织名称
    org_name: str | None = None
    # 是否为组织的所有着
    owner_flag: bool = False
    # 是否为组织的所有着
    admin_org: bool = False


class JwtPayload(BaseModel):
    user: JwtUser
    org: JwtOrg | None = None


class PasswordLogin(BaseModel):
    """账密登录
    """
    account: str = Field(description="账号")
    password_enc: str = Field(description="密码(加密)")


class SelectedOrg(BaseModel):
    """选择登录组织
    """
    org_id: int = Field(description="组织ID")


class AuthAPI:
    @staticmethod
    def jwt_encode(user: JwtUser, org: JwtOrg) -> str:
        """jwt构建
        """
        payload = JwtPayload(user=user, org=org).model_dump()
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
            return Rsp(code=AuthErrCode.ERR_ACCOUNT_STATUS_DISABLE, message="抱歉,您的账号或密码错误")

        if info["status"] == UserSettings.STATUS_DISABLE:
            return Rsp(code=AuthErrCode.ERR_PASSWORD_LOGIN, message="抱歉,您的账号已被停用")

        jwt_user = JwtUser(user_id=info["id"], nick_name=info["nick_name"])

        # 获取用户的组织信息(用户可选组织ID以及相关内容)
        stmt = select(
            Org.id,
            Org.name,
            Org.is_admin,
            Org.owner_id
        ).join_from(
            OrgUser, Org, OrgUser.org_id == Org.id
        ).where(
            and_(
                Org.deleted == False,
                Org.status == OrgSettings.STATUS_ENABLE,
                OrgUser.user_id == jwt_user.user_id
            )
        )
        result = ORM.all(db, stmt)

        jwt_org = JwtOrg(user_orgs=result)
        # 只有一个组织.直接登录
        if len(result) == 1:
            jwt_org.org_id = result[0]["id"]
            jwt_org.org_name = result[0]["name"]
            jwt_org.owner_flag = result[0]["owner_id"] == jwt_user.user_id
            jwt_org.admin_org = result[0]["is_admin"]

        return Rsp(data=AuthAPI.jwt_encode(jwt_user, jwt_org))

    @staticmethod
    def get_user_orgs(db: Session, user_id: int) -> Rsp:
        """获取用户所属组织
        """
        stmt = select(
            Org.id,
            Org.name,
        ).join_from(
            OrgUser, Org, OrgUser.org_id == Org.id
        ).where(
            and_(
                Org.deleted == False,
                Org.status == True,
                OrgUser.user_id == user_id
            )
        )

        result = ORM.all(db, stmt)

        return Rsp(data=result)

    @staticmethod
    def set_user_org(db: Session, user_id: int, data: SelectedOrg) -> Rsp:
        """设置用户的登录组织信息
        """

        stmt = select(
            User.nick_name, User.status,
            Org.name, Org.is_admin, Org.owner_id, Org.status.label("OrgStatus")
        ).join_from(
            OrgUser, User, User.id == OrgUser.user_id, isouter=True
        ).join(
            Org, OrgUser.org_id == Org.id, isouter=True
        ).where(
            and_(
                User.deleted == False, Org.deleted == False,
                OrgUser.user_id == user_id,
                OrgUser.org_id == data.org_id
            )
        )

        result = ORM.one(db, stmt)

        if result is None:
            return Rsp(code=1, message="无相关的用户组织信息")

        if result["status"] == UserSettings.STATUS_DISABLE:
            return Rsp(code=AuthErrCode.ERR_PASSWORD_LOGIN, message="抱歉,您的账号已被停用")

        if result["OrgStatus"] == OrgSettings.STATUS_DISABLE:
            return Rsp(code=1, message="组织已被停用")

        jwt_user = JwtUser(user_id=user_id, nick_name=result["nick_name"])
        owner_flag = result["owner_id"] == user_id
        jwt_org = JwtOrg(
            org_id=data.org_id, org_name=result["name"], owner_flag=owner_flag, admin_org=result["is_admin"])

        return Rsp(data=AuthAPI.jwt_encode(jwt_user, jwt_org))
