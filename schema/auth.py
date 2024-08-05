
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
            Org.org_name,
            Org.is_admin,
            Org.owner_id
        ).join_from(
            Org, OrgUser, Org.org_id == OrgUser.org_id
        ).where(and_(
            Org.deleted == False,
            OrgUser.status == OrgUserStatus.ENABLE.value,
            OrgUser.user_id == user_id
        ))

        return ORM.all(session, statement)

    @staticmethod
    def get_id_from_uuid(session: Session, user_uuid: str, org_uuid: str) -> dict | None:
        """获取用户ID和组织ID"""
        stmt = select(
            OrgUser.user_id,
            OrgUser.org_id
        ).join_from(
            OrgUser, User, OrgUser.user_id == User.user_id
        ).join(
            Org, OrgUser.org_id == Org.org_id
        ).where(and_(
            User.deleted == False,
            Org.deleted == False,
            User.user_uuid == user_uuid,
            Org.org_uuid == org_uuid
        ))

        return ORM.one(session, stmt)

    @staticmethod
    def get_org_user_info(actor: Actor) -> dict | None:
        stmt = select(
            OrgUser.user_name,
            OrgUser.avatar,
        ).where(
            OrgUser.user_id == actor.user_id,
            OrgUser.org_id == actor.org_id
        )

        return ORM.one(actor.session, stmt)

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
