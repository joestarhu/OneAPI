
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from jhu.orm import ORM

from api.model.user import User, UserAuth, UserAuthType
from api.model.org import Org, OrgUser, OrgUserStatus
from .base import Actor
from .errcode import APIErrors


class PasswordLogin(BaseModel):
    account: str = Field(description="用户账号")
    password_enc: str = Field(description="用户密码(hash加密)")


class SelectOrg(BaseModel):
    org_uuid: str = Field(description="组织UUID")


class AuthAPI:
    @staticmethod
    def get_password_info(session: Session, account: str = "") -> dict | None:
        """根据账号获取密码以及账号状态"""
        stmt = select(
            User.user_uuid,
            User.status,
            UserAuth.auth_value
        ).join_from(
            User, UserAuth, User.user_uuid == UserAuth.user_uuid
        ).where(and_(
            User.is_deleted == False,
            User.account == account,
            UserAuth.auth_type == UserAuthType.PASSWORD.value,
            UserAuth.auth_identify == ""
        ))

        return ORM.one(session, stmt)

    @staticmethod
    def get_user_orgs(actor: Actor):
        """获取用户所属的组织信息"""
        stmt = select(
            Org.org_uuid,
            Org.org_name,
            Org.is_admin,
            Org.owner_uuid
        ).join_from(
            Org, OrgUser, Org.org_uuid == OrgUser.org_uuid
        ).where(and_(
            Org.is_deleted == False,
            OrgUser.status == OrgUserStatus.ENABLE.value,
            OrgUser.user_uuid == actor.user_uuid
        ))

        return ORM.all(actor.session, stmt)

    @staticmethod
    def get_org_user_info(actor: Actor) -> dict | None:
        """获取组织登录用户的相关信息"""
        stmt = select(
            OrgUser.user_name,
            OrgUser.avatar,
        ).where(
            OrgUser.user_uuid == actor.user_uuid,
            OrgUser.org_uuid == actor.org_uuid
        )

        return ORM.one(actor.session, stmt)

    @staticmethod
    def check_user_org(actor: Actor, org_uuid: str) -> APIErrors:
        """用户登录组织是否合法"""
        stmt = select(
            Org.id
        ).join_from(
            OrgUser, Org, OrgUser.org_uuid == Org.org_uuid, isouter=True
        ).where(and_(
            Org.is_deleted == False,
            OrgUser.status == OrgUserStatus.ENABLE.value,
            OrgUser.user_uuid == actor.user_uuid,
            OrgUser.org_uuid == org_uuid
        ))

        if ORM.one(actor.session, stmt) == 0:
            return APIErrors.ORG_USER_DINIED

        return APIErrors.NO_ERROR
