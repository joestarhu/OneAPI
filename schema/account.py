from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import Session
from jhu.orm import ORM, ORMFormatRule, ORMCheckRule
from api.model.user import User, UserAuth, UserAuthType, UserStatus
from api.config.security import phone_encrypt, phone_decrypy, hash_api
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
    user_id: int = Field(description="用户ID")
    nick_name: str = Field(description="用户昵称")
    status: int = Field(description="用户状态")


class AccountDelete(BaseModel):
    user_id: int = Field(description="用户ID")


class AccountAPI:
    @staticmethod
    def get_account_list(actor: Actor, pagination: Pagination, phone: str = "", nick_name: str = "", status: int = None):
        """获取账户列表信息"""
        expressions = [expression for condition, expression in [
            (phone, User.phone.contains(phone_encrypt(phone))),
            (nick_name, User.nick_name.contains(nick_name)),
            (status is not None, User.status == status),
        ] if condition]

        statement = select(
            User.user_id,
            User.account,
            User.nick_name,
            User.phone,
            User.status,
            User.create_dt,
            User.update_dt
        ).where(and_(User.deleted == False, *expressions))

        return ORM.pagination(actor.session, statement, pagination.page_idx,
                              pagination.page_size, [User.create_dt.desc()], format_rules)

    @staticmethod
    def get_account_detail(actor: Actor, user_id: int):
        """获取账号详情"""
        statement = select(
            User.user_id,
            User.account,
            User.phone,
            User.nick_name,
            User.status
        ).where(and_(
            User.deleted == False,
            User.user_id == user_id
        ))

        return ORM.one(actor.session, statement, format_rules)

    @staticmethod
    def check_account_unique(session: Session, account: str = "", phone_hash: str = "", except_id: int = None) -> APIErrors | None:
        """唯一性校验"""

        except_expression = None if except_id is None else User.user_id != except_id

        orm_check_rules = [
            ORMCheckRule(APIErrors.PHONE_ALREADY_EXISTS,
                         User.phone == phone_hash),
            ORMCheckRule(APIErrors.ACCOUNT_ALREADY_EXISTS,
                         User.account == account),
        ]

        return ORM.check(session, orm_check_rules, except_expression)

    @staticmethod
    def create_account(session: Session, user: User, user_auth: UserAuth) -> APIErrors:
        """创建用户账号,所有需要加密存储的自动该函数会实施,入参无需处理"""
        try:

            user.phone = phone_encrypt(user.phone)
            if result := AccountAPI.check_account_unique(session, user.account, user.phone):
                return result

            session.add(user)
            session.flush()

            # 用户ID刷新
            user_auth.user_id = user.user_id

            # 加密存储密码
            if user_auth.auth_type == UserAuthType.PASSWORD.value:
                user_auth.auth_value = hash_api.hash(user_auth.auth_value)
            session.add(user_auth)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR

    @staticmethod
    def update_account(session: Session, user: User) -> APIErrors:
        """更新账户,仅更新 用户昵称和用户状态"""
        try:
            statement = update(User).where(User.user_id == user.user_id).values(
                nick_name=user.nick_name,
                status=user.status,
                update_id=user.update_id,
                update_dt=user.update_dt
            )
            session.execute(statement)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR

    @staticmethod
    def delete_account(session: Session, user_id: int) -> APIErrors:
        """删除账户"""

        try:
            # 构建一个无意义的删除字符
            delete_uuid = "del_"+"".join(str(uuid4()).split("-"))

            for statement in [
                update(User).where(User.user_id == user_id).values(
                    deleted=True, account=delete_uuid, phone=delete_uuid),
                delete(UserAuth).where(UserAuth.user_id == user_id)
            ]:
                session.execute(statement)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR
