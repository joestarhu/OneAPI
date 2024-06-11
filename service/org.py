from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import and_, select, update
from sqlalchemy.orm.session import Session
from api.config.security import FieldSecurity, hash_api  # noqa
from api.config.settings import settings  # noqa
from api.model.user import User, UserSettings  # noqa
from api.model.org import OrgSettings, Org, OrgUser  # noqa
from api.service.base import ORM, Rsp, RspError, Pagination, ActInfo  # noqa


class OrgList(Pagination):
    name: str | None = None
    status: int | None = None


class OrgCreate(BaseModel):
    name: str = Field(description="组织名称")
    owner_id: int = Field(description="组织所有者ID")
    status: int = Field(description="组织状态")
    remark: str | None = Field(default=None, description="组织备注描述")


class OrgUpdate(BaseModel):
    org_id: int = Field(description="组织ID")
    name: str = Field(description="组织名称")
    owner_id: int = Field(description="组织所有者ID")
    status: int = Field(description="组织状态")
    remark: str | None = Field(default=None, description="组织备注描述")


class OrgDelete(BaseModel):
    org_id: int = Field(description="组织ID")


class OrgAPI:
    @staticmethod
    def unique_chk(db: Session, name: str, except_id: int = None) -> Rsp | None:
        if except_id is None:
            expression = None
        else:
            expression = Org.id != except_id

        rules = [
            ("组织名称已被使用", and_(Org.name == name, Org.deleted == False)),
        ]

        return ORM.unique_chk(db, rules, expression)

    @staticmethod
    def get_list(db: Session, data: OrgList) -> Rsp:
        stmt = select(
            Org.id,
            Org.name,
            Org.status,
            Org.owner_id,
            User.nick_name.label("owner_name"),
            Org.remark,
            Org.update_dt,
            Org.create_dt
        ).join_from(
            Org, User, Org.owner_id == User.id, isouter=True
        ).where(
            Org.deleted == False
        )

        if data.name:
            stmt = stmt.where(Org.name.contains(data.name))

        if data.status is not None:
            stmt = stmt.where(Org.status == data.status)

        result = ORM.pagination(db, stmt, page_idx=data.page_idx,
                                page_size=data.page_size, order=[Org.create_dt.desc()])

        return Rsp(data=result)

    @staticmethod
    def get_detail(db: Session, org_id: int) -> Rsp:
        """获取详情
        """
        stmt = select(
            Org.id,
            Org.name,
            Org.status,
            Org.owner_id,
            Org.remark
        ).where(
            Org.id == org_id
        )

        result = ORM.one(db, stmt)

        return Rsp(data=result)

    @staticmethod
    def create_org(db: Session, act: ActInfo, data: OrgCreate) -> Rsp:
        # 唯一性检测
        if rsp := OrgAPI.unique_chk(db, data.name):
            return rsp

        try:
            org = Org(**data.model_dump(), **act.insert_info)
            db.add(org)
            db.flush()

            org_user = OrgUser(org_id=org.id, user_id=org.owner_id)
            db.add(org_user)

            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f"{e}")

        return Rsp()

    @staticmethod
    def update_org(db: Session, act: ActInfo, data: OrgUpdate) -> Rsp:
        # 唯一性检测
        if rsp := OrgAPI.unique_chk(db, data.name, data.org_id):
            return rsp

        # 更新相关数据内容
        try:
            stmt = update(Org).where(
                Org.id == data.org_id
            ).values(**data.model_dump(exclude=["org_id"]), **act.update_info)
            db.execute(stmt)

            stmt = select(OrgUser.id).where(
                and_(
                    OrgUser.user_id == data.owner_id,
                    OrgUser.org_id == data.org_id
                )
            )

            if ORM.counts(db, stmt) == 0:
                org_user = OrgUser(org_id=data.org_id, user_id=data.owner_id)
                db.add(org_user)

            db.commit()
        except Exception as e:
            db.rollback()
            raise RspError(data=f"{e}")

        return Rsp()

    @staticmethod
    def delete_org(db: Session, act: ActInfo, data: OrgDelete) -> Rsp:
        stmt = select(Org.is_admin).where(
            and_(
                Org.id == data.org_id,
                Org.is_admin == True
            )
        )

        if ORM.counts(db, stmt) == 1:
            return Rsp(code=1, message="平台级组织不允许删除")

        """
            删除时候,组织名称随机化(唯一键约束)
            不删除UserOrg,是为了后续的数据恢复,误删组织后,用户等数据还是存在可以恢复的
        """
        stmt = update(Org).where(Org.id == data.org_id).values(
            name=uuid4(), deleted=True, **act.update_info)

        ORM.commit(db, stmt)

        return Rsp()
