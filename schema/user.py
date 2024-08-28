from sqlalchemy import select, and_
from jhu.orm import ORM, ORMFormatRule
from api.config.security import phone_decrypy, phone_encrypt
from api.model.user import User
from .base import Actor, Pagination


format_rules = [ORMFormatRule("phone", phone_decrypy)]


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
        expression_list = [
            (phone_enc, User.phone_enc.contains(phone_enc)),
            (nick_name, User.nick_name.contains(nick_name)),
            (status is not None, User.status == status),
        ]

        expressions = [expression for condtion,
                       expression in expression_list if condtion]

        stmt = select(
            User.user_uuid,
            User.account,
            User.nick_name,
            User.phone_enc.label("phone"),
            User.status,
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
            User.status,
        ).where(and_(
            User.is_deleted == False,
            User.user_uuid == user_uuid
        ))

        return ORM.one(actor.session, stmt, format_rules)
