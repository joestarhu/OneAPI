from pydantic import BaseModel, Field, validator
from sqlalchemy import select, update, delete, and_
from jhu.orm import ORM, ORMFormatRule, ORMCheckRule
from api.config.settings import settings
from api.config.security import phone_decrypy, phone_encrypt, generate_uuid_str, hash_api
from api.model.user import User, UserAuth, UserAuthType, UserStatus
from api.schema.errcode import APIErrors
from .base import Actor, Pagination, Session


class AccountCreate(BaseModel):
    account: str = Field(description="账号")
    phone: str = Field(description="手机号", pattern="^1[3-9]\d{9}$")
    nick_name: str = Field(description="用户昵称")
    status: int = Field(description="用户状态")

    @validator("status")
    def status_validator(cls, value):
        if value not in UserStatus:
            raise ValueError("用户状况必须是0或者1")
        return value


class AccountUpdate(BaseModel):
    user_uuid: str = Field(descrixption="用户UUID")
    nick_name: str = Field(description="用户昵称")
    status: int = Field(description="用户状态")

    @validator("status")
    def status_validator(cls, value):
        if value not in UserStatus:
            raise ValueError("用户状况必须是0或者1")
        return value


class AccountDelete(BaseModel):
    user_uuid: str = Field(descrixption="用户UUID")


format_rules = [ORMFormatRule("phone", phone_decrypy)]


def check_account_unique(session: Session, phone_enc: str, account: str, user_uuid: str = None) -> APIErrors:
    """账号唯一性判断"""
    except_expression = None if user_uuid is None else User.user_uuid != user_uuid

    orm_check_rules = [
        ORMCheckRule(APIErrors.USER_PHONE_ALREADY_EXISTS,
                     User.phone_enc == phone_enc),
        ORMCheckRule(APIErrors.USER_ACCOUNT_ALREADY_EXISTS,
                     User.account == account),
    ]

    return ORM.check(session, orm_check_rules, except_expression)


class UserAPI:
    @staticmethod
    def get_account_list(actor: Actor,
                         pagination: Pagination,
                         phone: str = "",
                         nick_name: str = "",
                         status: int | None = None,
                         ) -> list:
        """获取账户list"""

        # 加密手机号
        phone_enc = phone_encrypt(phone) if phone else ""

        # 拼接查询条件
        expressions = [expression for condtion,
                       expression in [
                           (phone_enc, User.phone_enc.contains(phone_enc)),
                           (nick_name, User.nick_name.contains(nick_name)),
                           (status is not None, User.user_status == status),
                       ] if condtion]

        stmt = select(
            User.user_uuid,
            User.account,
            User.nick_name,
            User.phone_enc.label("phone"),
            User.user_status,
            User.created_at,
            User.updated_at,
        ).where(and_(
            User.is_deleted == False,
            *expressions
        ))

        return ORM.pagination(actor.session, stmt, pagination.page_idx, pagination.page_size, [User.created_at.desc()], format_rules)

    @staticmethod
    def get_account_detail(actor: Actor,
                           user_uuid: str
                           ) -> dict | None:
        """获取账户详细信息"""
        stmt = select(
            User.user_uuid,
            User.account,
            User.nick_name,
            User.phone_enc.label("phone"),
            User.user_status,
        ).where(and_(
            User.is_deleted == False,
            User.user_uuid == user_uuid
        ))

        return ORM.one(actor.session, stmt, format_rules)

    @staticmethod
    def create_account(data: AccountCreate,
                       actor: Actor
                       ) -> APIErrors:
        """创建用户账号,所有需要加密存储的自动该函数会实施,入参无需处理"""
        try:
            session = actor.session
            phone_enc = phone_encrypt(data.phone)

            # 唯一性判断
            if result := check_account_unique(session, phone_enc, data.account):
                return result

            user_uuid = generate_uuid_str()
            user = User(user_uuid=user_uuid,
                        phone_enc=phone_enc,
                        **data.model_dump(exclude=["phone"])
                        )

            user_auth = UserAuth(
                user_uuid=user_uuid,
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
    def update_account(data: AccountUpdate,
                       actor: Actor
                       ) -> APIErrors:
        """更新账户,仅更新 用户昵称和用户状态"""
        try:
            session = actor.session

            # if AccountAPI.check_superadmin(session, data.user_uuid) == True:
            #     return APIErrors.USER_ADMIN_CTRL_DINED

            stmt = update(User).where(
                User.user_uuid == data.user_uuid
            ).values(
                nick_name=data.nick_name,
                user_status=data.status
            )

            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR

    @staticmethod
    def delete_account(data: AccountDelete,
                       actor: Actor
                       ) -> APIErrors:
        """删除账户"""
        try:
            session = actor.session
            delete_uuid = data.user_uuid

            # if AccountAPI.check_superadmin(session, delete_uuid) == True:
            #     return APIErrors.USER_ADMIN_CTRL_DINED

            for statement in [
                update(User).where(User.user_uuid == delete_uuid).values(is_deleted=True,
                                                                         account=delete_uuid,
                                                                         phone_enc=delete_uuid),
                delete(UserAuth).where(UserAuth.user_uuid == delete_uuid)
            ]:
                session.execute(statement)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        return APIErrors.NO_ERROR
