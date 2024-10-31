from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, update, delete, and_
from jhu.orm import ORM, ORMFormatRule, ORMCheckRule
from api.config.settings import settings
from api.config.security import phone_decrypy, phone_encrypt, generate_uuid_str, hash_api
from api.model.user import User, UserAuth, UserAuthType, UserStatus
from api.model.org import Org, OrgUser
from api.schema.errcode import APIErrors
from .base import Actor, Pagination, Session


class AccountCreate(BaseModel):
    account: str = Field(description="账号")
    nick_name: str = Field(description="用户昵称")
    phone: str = Field(default="", description="手机号",
                       pattern=r"^1[3-9]\d{9}$|^$")
    user_status: int = Field(description="用户状态")

    @field_validator("user_status")
    def status_validator(cls, value):
        if value not in UserStatus:
            raise ValueError("用户状况必须是0或者1")
        return value


class AccountUpdate(BaseModel):
    user_uuid: str = Field(descrixption="用户UUID")
    nick_name: str = Field(description="用户昵称")
    user_status: int = Field(description="用户状态")

    @field_validator("user_status")
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
        ORMCheckRule(APIErrors.USER_ACCOUNT_ALREADY_EXISTS,
                     User.account == account),
    ]

    if phone_enc:
        orm_check_rules.append(
            ORMCheckRule(APIErrors.USER_PHONE_ALREADY_EXISTS,
                         User.phone_enc == phone_enc)
        )

    return ORM.check(session, orm_check_rules, except_expression)


def check_superadmin(session: Session, user_uuid: str) -> bool:
    """判断是否是超级管理员"""
    stmt = select(Org.id).where(and_(Org.is_deleted == False,
                                     Org.is_admin == True,
                                     Org.owner_uuid == user_uuid
                                     ))

    return True if ORM.counts(session, stmt) else False


def check_org_owner(session: Session, user_uuid: str) -> bool:
    """判断是否是组织的所有者"""
    stmt = select(Org.id).where(and_(Org.is_deleted == False,
                                     Org.owner_uuid == user_uuid
                                     ))

    return True if ORM.counts(session, stmt) else False


class UserAPI:
    @staticmethod
    def get_account_status_info() -> list:
        UserStatus.ENABLE.value

    @staticmethod
    def get_account_list(actor: Actor,
                         pagination: Pagination,
                         account: str = "",
                         nick_name: str = "",
                         phone: str = "",
                         status: int | None = None,
                         ) -> list:
        """获取账户list"""

        # 加密手机号
        phone_enc = phone_encrypt(phone) if phone else ""

        # 拼接查询条件
        expressions = [expression for condtion,
                       expression in [
                           (account, User.account.ilike(f"%{account}%")),
                           (nick_name, User.nick_name.ilike(f"%{nick_name}%")),
                           (phone_enc, User.phone_enc.ilike(f"%{phone_enc}%")),
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
            User.created_at,
            User.updated_at
        ).where(and_(
            User.is_deleted == False,
            User.user_uuid == user_uuid
        ))

        return ORM.one(actor.session, stmt, format_rules)

    @staticmethod
    def get_account_orgs(actor: Actor,
                         pagination: Pagination,
                         user_uuid: str) -> list:
        """获取账户组织信息"""
        stmt = select(
            Org.org_name,
            Org.org_status,
            OrgUser.org_user_status,
        ).join(
            OrgUser, OrgUser.org_uuid == Org.org_uuid
        ).where(and_(
            Org.is_deleted == False,
            OrgUser.user_uuid == user_uuid
        ))

        return ORM.pagination(actor.session, stmt, page_idx=pagination.page_idx, page_size=pagination.page_size)

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

            if check_superadmin(session, data.user_uuid):
                return APIErrors.USER_ADMIN_CTRL_DINED

            stmt = update(User).where(
                User.user_uuid == data.user_uuid
            ).values(
                nick_name=data.nick_name,
                user_status=data.user_status
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

            for chk_func, err_info in [
                (check_superadmin, APIErrors.USER_ADMIN_CTRL_DINED),
                (check_org_owner, APIErrors.USER_ORG_OWN_DELETE_DINED),
            ]:
                if chk_func(session, delete_uuid):
                    return err_info

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
