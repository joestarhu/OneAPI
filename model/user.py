from uuid import uuid4
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Integer, SmallInteger, String, UniqueConstraint, select, delete, update, and_
from sqlalchemy.orm import Mapped as M, mapped_column as mc, Session
from jhu.orm import ORM, ORMCheckRule
from api.config.security import FieldSecurity, hash_api
from api.config.errcode import ErrCode
from .base import ModelBase


class UserSettings:
    """用户配置
    """

    # 用户状态:停用
    STATUS_DISABLE: int = 0
    # 用户状态:启用
    STATUS_ENABLE: int = 1

    # 用户认证类型:密码
    AUTH_TYPE_PASSWORD: int = 0


class User(ModelBase):
    __tablename__ = "t_user"
    __table_args__ = (
        {"comment": "用户信息"}
    )

    account: M[str] = mc(String(128), unique=True, comment="用户账号,全局唯一")
    phone: M[str] = mc(String(256), unique=True, comment="用户手机号,加密存储,全局唯一")
    nick_name: M[str] = mc(String(256), comment="用户昵称")
    status: M[int] = mc(
        SmallInteger, default=UserSettings.STATUS_ENABLE, comment="用户状态")
    deleted: M[bool] = mc(Boolean, default=False, comment="逻辑删除标志,True表示逻辑已删除")


class UserAuth(ModelBase):
    __tablename__ = "t_user_auth"
    __table_args__ = (
        UniqueConstraint("user_id", "auth_type",
                         "auth_identify", name="uni_user_auth"),
        {"comment": "用户认证信息"}
    )

    user_id: M[int] = mc(BigInteger, comment="用户ID")
    auth_type: M[int] = mc(
        Integer, default=UserSettings.AUTH_TYPE_PASSWORD, comment="认证类型")
    auth_identify: M[str] = mc(String(128), default="", comment="认证标识")
    auth_value: M[str] = mc(String(256), comment="认证值")


class UserAPI:
    @staticmethod
    def unique_check(db: Session, account: str, phone: str, user_id: int = None):
        except_expression = None
        if user_id is not None:
            except_expression = User.id != user_id

        check_rules = [
            ORMCheckRule(ErrCode.ACCOUNT_ALREADY_EXISTS,
                         User.account == account),
            ORMCheckRule(ErrCode.PHONE_ALREADY_EXISTS,
                         User.phone == phone)
        ]

        return ORM.check(db, check_rules, except_expression)

    @staticmethod
    def create(db: Session, user: User, user_auth: UserAuth) -> ErrCode:
        try:
            # 手机号先进行加密处理
            user.phone = FieldSecurity.phone_encrypt(user.phone)

            # 唯一性检测
            if err_code := UserAPI.unique_check(db, user.account, user.phone):
                return err_code

            db.add(user)
            db.flush()

            user_auth.user_id = user.id
            if UserSettings.AUTH_TYPE_PASSWORD == user_auth.auth_type:
                # 加密处理密码数据
                user_auth.auth_value = hash_api.hash(user_auth.auth_value)

            db.add(user_auth)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

        return ErrCode.NO_ERROR

    @staticmethod
    def update(db: Session, user: User) -> ErrCode:
        """
        Args:
            user: 仅需要填入id,update_id和update_dt,nick_name, status即可;
        """
        stmt = update(User).where(User.id == user.id).values(
            update_id=user.update_id,
            update_dt=user.update_dt,
            nick_name=user.nick_name,
            status=user.status
        )

        try:
            db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

        return ErrCode.NO_ERROR

    @staticmethod
    def delete(db: Session, user: User) -> ErrCode:
        """
        Args:
            user: 仅需要填入id,update_id和update_dt即可
        """
        try:
            # 删除用的替代字符.
            delete_value = str(uuid4())

            for stmt in [
                delete(UserAuth).where(UserAuth.user_id == user.id),
                update(User).where(User.id == user.id).values(
                    deleted=True,
                    account=delete_value,
                    phone=delete_value,
                    update_id=user.update_id,
                    update_dt=user.update_dt
                )
            ]:
                db.execute(stmt)

            db.commit()
        except Exception as e:
            db.rollback()
            raise e

        return ErrCode.NO_ERROR

    @staticmethod
    def get_user_auth_info(db: Session, auth_type: int, auth_identify: str, account: str) -> dict | None:
        """根据账号或手机号获取

        Args:
            db: 数据库会话
            auth_type: 认证类型
            auth_identify: 认证标识
            account: 用户账户
        """
        expression = and_(
            User.deleted == False,
            User.account == account,
            UserAuth.auth_type == auth_type,
            UserAuth.auth_identify == auth_identify
        )

        stmt = select(User.id, User.status, UserAuth.auth_value).join_from(
            User, UserAuth, User.id == UserAuth.user_id
        ).where(expression)

        return ORM.one(db, stmt)
