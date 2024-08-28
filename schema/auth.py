# from .base import Actor, Session
# from .errcode import APIErrors
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from jhu.orm import ORM
from api.model.user import User, UserAuth, UserAuthType, UserStatus
from api.model.org import Org, OrgUser, OrgStatus, OrgUserStatus
from api.schema.base import Actor
from .base import Session


class PasswordLogin(BaseModel):
    account: str = Field(description="用户账号")
    password_enc: str = Field(description="用户密码(hash加密)")

# class ChooseOrg(BaseModel):
#     org_uuid: str = Field(description="组织UUID")


class AuthAPI:
    @staticmethod
    def get_account_auth_info(session: Session,
                              account: str,
                              auth_type: UserAuthType = UserAuthType.PASSWORD,
                              auth_identify: str = ""
                              ) -> dict | None:
        """获取账户的认证信息"""
        stmt = select(
            User.user_uuid,
            User.user_status,
            UserAuth.auth_value
        ).join_from(
            User, UserAuth, User.user_uuid == UserAuth.user_uuid
        ).where(and_(
            User.is_deleted == False,
            User.account == account,
            UserAuth.auth_type == auth_type.value,
            UserAuth.auth_identify == auth_identify
        ))

        return ORM.one(session, stmt)

    @staticmethod
    def get_user_org_list(session: Session,
                          user_uuid: str
                          ) -> list:
        """获取用户的组织信息"""
        stmt = select(
            Org.org_uuid,
            Org.owner_uuid,
            OrgUser.org_user_status
        ).join_from(
            Org, OrgUser, Org.org_uuid == OrgUser.org_uuid
        ).where(and_(
            Org.is_deleted == False,
            Org.org_status == OrgStatus.ENABLE.value,
            OrgUser.user_uuid == user_uuid
        ))

        return ORM.all(session, stmt)

    @staticmethod
    def get_org_user_info(actor: Actor) -> dict | None:
        """获取登录组织用户的信息"""
        stmt = select(
            OrgUser.org_user_name,
            OrgUser.org_user_avatar_url
        ).where(and_(
            OrgUser.org_uuid == actor.org_uuid,
            OrgUser.user_uuid == actor.user_uuid
        ))

        return ORM.one(actor.session, stmt)

    @staticmethod
    def get_org_name(actor: Actor) -> dict | None:
        """获取已登录组织的名称"""
        stmt = select(
            Org.org_name
        ).where(Org.org_uuid == actor.org_uuid)

        return ORM.one(actor.session, stmt)

# class AuthAPI:
#     @staticmethod
#     def check_login_avaiable(session: Session, user_uuid: str, org_uuid: str) -> bool:
#         """判断用户,组织是否正常状态"""
#         stmt = select(
#             OrgUser.id
#         ).join_from(
#             OrgUser, User, OrgUser.user_uuid == User.user_uuid
#         ).join(
#             Org, OrgUser.org_uuid == Org.org_uuid
#         ).where(and_(
#             Org.is_deleted == False,
#             Org.status == OrgStatus.ENABLE.value,
#             User.is_deleted == False,
#             User.status == UserStatus.ENABLE.value,
#             OrgUser.status == OrgUserStatus.ENABLE.value,
#             OrgUser.user_uuid == user_uuid,
#             OrgUser.org_uuid == org_uuid
#         ))

#         return True if ORM.counts(session, stmt) > 0 else False

#     @staticmethod
#     def get_password_info(session: Session, account: str = "") -> dict | None:
#         """根据账号获取密码以及账号状态"""
#         stmt = select(
#             User.user_uuid,
#             User.status,
#             UserAuth.auth_value
#         ).join_from(
#             User, UserAuth, User.user_uuid == UserAuth.user_uuid
#         ).where(and_(
#             User.is_deleted == False,
#             User.account == account,
#             UserAuth.auth_type == UserAuthType.PASSWORD.value,
#             UserAuth.auth_identify == ""
#         ))

#         return ORM.one(session, stmt)

#     @staticmethod
#     def get_user_orgs(actor: Actor):
#         """获取用户所属的组织列表信息"""
#         stmt = select(
#             Org.org_uuid,
#             Org.org_name,
#             Org.is_admin,
#             Org.owner_uuid
#         ).join_from(
#             Org, OrgUser, Org.org_uuid == OrgUser.org_uuid
#         ).where(and_(
#             Org.is_deleted == False,
#             Org.status == OrgStatus.ENABLE.value,
#             OrgUser.status == OrgUserStatus.ENABLE.value,
#             OrgUser.user_uuid == actor.user_uuid
#         ))

#         return ORM.all(actor.session, stmt)

#     @staticmethod
#     def get_org_user_info(actor: Actor) -> dict | None:
#         """获取组织登录用户的相关信息"""
#         stmt = select(
#             OrgUser.user_name,
#             OrgUser.avatar,
#         ).where(
#             OrgUser.user_uuid == actor.user_uuid,
#             OrgUser.org_uuid == actor.org_uuid
#         )

#         return ORM.one(actor.session, stmt)

#     @staticmethod
#     def get_user_org(actor: Actor, org_uuid: str) -> dict | None:
#         """获取用户指定的组织信息"""
#         stmt = select(
#             Org.org_uuid,
#             Org.is_admin,
#             Org.owner_uuid
#         ).join_from(
#             OrgUser, Org, OrgUser.org_uuid == Org.org_uuid, isouter=True
#         ).where(and_(
#             Org.is_deleted == False,
#             OrgUser.status == OrgUserStatus.ENABLE.value,
#             OrgUser.user_uuid == actor.user_uuid,
#             OrgUser.org_uuid == org_uuid
#         ))

#         return ORM.one(actor.session, stmt)
