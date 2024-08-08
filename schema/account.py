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


# 手机号格式化函数(中间4位脱敏)
format_rules = [ORMFormatRule("phone", phone_decrypy)]


class AccountCreate(BaseModel):
    """创建账户"""
    account: str = Field(description="账号")
    phone: str = Field(description="手机号")
    nick_name: str = Field(description="用户昵称")
    status: int = Field(description="用户状态")


class AccountUpdate(BaseModel):
    user_uuid: str = Field(descrixption="用户UUID")
    nick_name: str = Field(description="用户昵称")
    status: int = Field(description="用户状态")


class AccountDelete(BaseModel):
    user_uuid: str = Field(descrixption="用户UUID")


class AccountAPI:
    @staticmethod
    def get_account_list(actor: Actor, pagination: Pagination, phone: str = "", nick_name: str = "", status: int = None):
        """获取账户列表信息"""
        expressions = [expression for condition, expression in [
            (phone, User.phone.contains(phone_encrypt(phone))),
            (nick_name, User.nick_name.contains(nick_name)),
            (status is not None, User.status == status),
        ] if condition]

        stmt = select(
            User.user_uuid,
            User.account,
            User.nick_name,
            User.phone,
            User.status,
            User.created_at,
            User.updated_at
        ).where(and_(User.is_deleted == False, *expressions))

        return ORM.pagination(actor.session, stmt, pagination.page_idx,
                              pagination.page_size, [User.created_at.desc()], format_rules)

    @staticmethod
    def get_account_detail(actor: Actor, user_uuid: str):
        """获取账号详情"""
        stmt = select(
            User.account,
            User.phone,
            User.nick_name,
            User.status
        ).where(and_(
            User.is_deleted == False,
            User.user_uuid == user_uuid
        ))

        return ORM.one(actor.session, stmt, format_rules)

    @staticmethod
    def check_account_unique(session: Session, account: str = "", phone_hash: str = "", except_uuid: str = None) -> APIErrors | None:
        """唯一性校验"""

        except_expression = None if except_uuid is None else User.user_uuid != except_uuid

        orm_check_rules = [
            ORMCheckRule(APIErrors.PHONE_ALREADY_EXISTS,
                         User.phone == phone_hash),
            ORMCheckRule(APIErrors.ACCOUNT_ALREADY_EXISTS,
                         User.account == account),
        ]

        return ORM.check(session, orm_check_rules, except_expression)

    @staticmethod
    def check_superadmin(session: Session, user_uuid: str) -> bool:
        result = False

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

        if ORM.counts(session, stmt) > 0:
            result = True

        return result

    @staticmethod
    def create_account(actor: Actor, data: AccountCreate) -> APIErrors:
        """创建用户账号,所有需要加密存储的自动该函数会实施,入参无需处理"""
        try:
            session = actor.session
            phone_enc = phone_encrypt(data.phone)

            if result := AccountAPI.check_account_unique(session, data.account, phone_enc):
                return result

            user = User(
                user_uuid=generate_uuid_str(),
                phone=phone_enc,
                **data.model_dump(exclude=["phone"])
            )

            user_auth = UserAuth(
                user_uuid=user.user_uuid,
                auth_type=UserAuthType.PASSWORD.value,
                auth_identify="",
                auth_value=hash_api.hash(settings.default_passwd)
            )

            session.add_all([user, user_auth])
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR

    @staticmethod
    def update_account(actor: Actor, data: AccountUpdate) -> APIErrors:
        """更新账户,仅更新 用户昵称和用户状态"""

        try:
            session = actor.session

            if AccountAPI.check_superadmin(session, data.user_uuid) == True:
                return APIErrors.SUPERADMIN_DINIED

            stmt = update(User).where(
                User.user_uuid == data.user_uuid
            ).values(
                nick_name=data.nick_name,
                status=data.status
            )

            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR

    @staticmethod
    def delete_account(actor: Actor, data: AccountDelete) -> APIErrors:
        """删除账户"""

        try:
            session = actor.session
            delete_uuid = data.user_uuid

            if AccountAPI.check_superadmin(session, delete_uuid) == True:
                return APIErrors.SUPERADMIN_DINIED

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
