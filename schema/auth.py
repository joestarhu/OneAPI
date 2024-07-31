
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from jhu.orm import ORM

from api.model.user import User, UserAuth, UserAuthType
from api.model.org import Org, OrgUser, OrgUserStatus
from .errcode import APIErrors


class PasswordLogin(BaseModel):
    account: str = Field(description="用户账号")
    password_enc: str = Field(description="用户密码(hash加密)")


class SelectOrg(BaseModel):
    org_id: int = Field(description="组织ID")


class AuthAPI:
    @staticmethod
    def get_password_info(session: Session, account: str = "") -> dict | None:
        """根据账号获取密码以及账号状态"""
        stmt = select(
            User.user_id,
            User.user_uuid,
            User.status,
            UserAuth.auth_value
        ).join_from(
            User, UserAuth, User.user_id == UserAuth.user_id
        ).where(and_(
            User.deleted == False,
            User.account == account,
            UserAuth.auth_type == UserAuthType.PASSWORD.value,
            UserAuth.auth_identify == ""
        ))

        return ORM.one(session, stmt)

    @staticmethod
    def get_user_orgs(session: Session, user_id: int):
        """获取用户所属的组织信息"""
        statement = select(
            Org.org_uuid,
            Org.org_name
        ).join_from(
            Org, OrgUser, Org.org_id == OrgUser.org_id
        ).where(and_(
            Org.deleted == False,
            OrgUser.status == OrgUserStatus.ENABLE.value,
            OrgUser.user_id == user_id
        ))

        return ORM.all(session, statement)

#     @staticmethod
#     def set_user_org(session: Session, user_id: int, org_id: int) -> APIErrors:
#         """设置用户登录的组织信息"""
#         stmt = select(
#             OrgUser.id
#         ).join_from(
#             Org, OrgUser, Org.org_id == OrgUser.org_id
#         ).where(and_(
#             Org.deleted == False,
#             OrgUser.status == OrgUserStatus.ENABLE.value,
#             OrgUser.org_id == org_id,
#             OrgUser.user_id == user_id
#         ))

#         if ORM.counts(session, stmt) != 1:
#             return APIErrors.WRONG_ORG_ACCOUNT

#         return APIErrors.NO_ERROR
