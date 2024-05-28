from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.orm.session import Session
from api.config.security import FieldSecurity  # noqa
from api.model.user import User, UserAuth, UserSettings  # noqa
from api.service.base import ORM, Rsp, Pagination  # noqa


class AccountList(Pagination):
    phone: str | None = Field(description="手机号")
    nick_name: str | None = Field(description="用户昵称")
    status: int | None = Field(description="用户状态")


class AccountCreate(BaseModel):
    account: str = Field(description="账号")
    phone: str = Field(description="手机号")
    nick_name: str = Field(description="用户昵称")
    status: int = Field(description="用户状态")


class AccountAPI:
    @staticmethod
    def unique_chk(db: Session, account: str, phone_enc: str, except_id: int = None) -> Rsp | None:
        """判断账户唯一性

        Args:
            db: 数据库会话
            account: 账户
            phone_enc: 加密的手机号
            except_id: 不在唯一性判定内的账户ID,用于修改

        Return:
            None: 成功,无重复数据
            Rsp: 失败,出现重复数据
        """
        if except_id is None:
            expression = None
        else:
            expression = User.id != except_id

        rules = [
            ("账号已被使用", and_(User.account == account, User.deleted == False)),
            ("手机号已被使用", and_(User.phone == phone_enc, User.deleted == False)),
        ]

        return ORM.unique_chk(db, rules, expression)

    @staticmethod
    def get_list(db: Session, data: AccountList) -> Rsp:
        """获取账户列表信息

        Args:
            db: 数据库会话
            data: 查询数据对象

        Return:
            Rsp:返回HttpResponse;如有失败会抛出异常
        """

        # 查询用户的信息
        stmt = select(
            User.id, User.phone, User.account, User.nick_name, User.status, User.update_dt, User.create_dt
        ).where(
            User.deleted == False
        )

        # 模糊匹配用户昵称
        if data.nick_name:
            stmt = stmt.where(User.nick_name.contains(data.nick_name))

        # 模糊匹配用户手机号
        if data.phone:
            stmt = stmt.where(
                User.phone.contains(FieldSecurity.phone_encrypt(data.phone))
            )

        # 精准匹配用户状态
        if data.status is not None:
            stmt = stmt.where(User.status == data.status)

        # 用户创建时间倒序排序分页查询
        result = ORM.pagination(db, stmt, page_idx=data.page_idx, page_size=data.page_size,
                                order=[User.create_dt.desc()],
                                fmt_rules=[
                                    ('phone', FieldSecurity.phone_decrypt)]
                                )

        return Rsp(data=result)
