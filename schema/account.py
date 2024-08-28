from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import Session
from jhu.orm import ORM, ORMFormatRule, ORMCheckRule
from api.model.user import User, UserAuth, UserAuthType, UserStatus
from api.model.org import Org, OrgUser
from api.config.security import phone_encrypt, phone_decrypy, generate_uuid_str, hash_api
from api.config.settings import settings
from .base import Pagination, Actor
from .errcode import APIErrors


class AccountDelete:
    ...


class AccountAPI:
    @staticmethod
    def check_superadmin(session: Session, user_uuid: str) -> bool:
        stmt = select(
            Org.is_admin
        ).join_from(
            Org, User, Org.owner_uuid == User.user_uuid
        ).where(and_(
            Org.is_admin == True,
            Org.is_deleted == False,
            User.is_deleted == False,
            User.user_uuid == user_uuid
        ))

        return True if ORM.counts(session, stmt) > 0 else False

    @staticmethod
    def delete_account(actor: Actor, data: AccountDelete) -> APIErrors:
        """删除账户"""

        try:
            session = actor.session
            delete_uuid = data.user_uuid

            if AccountAPI.check_superadmin(session, delete_uuid) == True:
                return APIErrors.USER_ADMIN_CTRL_DINED

            for statement in [
                update(User).where(User.user_uuid == delete_uuid).values(is_deleted=True,
                                                                         account=delete_uuid,
                                                                         phone=delete_uuid),
                delete(UserAuth).where(UserAuth.user_uuid == delete_uuid)
            ]:
                session.execute(statement)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR
