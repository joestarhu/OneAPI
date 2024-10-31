from pydantic import BaseModel, Field
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import Session
from jhu.orm import ORM, ORMCheckRule
from api.model.org import Org, OrgUser, OrgUserRole, OrgStatus
from api.model.user import User, UserStatus
from api.config.security import generate_uuid_str
from .user import UserAPI
from .base import Pagination, Actor
from .errcode import APIErrors


class OrgCreate(BaseModel):
    org_name: str = Field(description="组织名称")
    owner_uuid: str = Field(description="组织所有者UUID")
    org_remark: str = Field(description="组织备注")
    org_status: int = Field(default=OrgStatus.ENABLE.value, description="组织状态")


class OrgUpdate(BaseModel):
    org_uuid: str = Field(description="组织UUID")
    org_name: str = Field(description="组织名称")
    owner_uuid: str = Field(description="组织所有者UUID")
    org_remark: str = Field(description="组织备注")
    org_status: int = Field(description="组织状态")


class OrgDelete(BaseModel):
    org_uuid: str = Field(description="组织UUID")


class OrgAPI:
    @staticmethod
    def get_org_list(actor: Actor, pagination: Pagination, org_name: str = "",  org_status: int = None):
        expressions = [expression for condition, expression in [
            (org_name, Org.org_name.ilike(f"%{org_name}%")),
            (org_status is not None, Org.org_status == org_status),
        ] if condition]

        stmt = select(
            Org.org_uuid,
            Org.org_name,
            User.nick_name.label("owner_name"),
            Org.org_status,
            Org.org_remark,
            Org.created_at,
            Org.updated_at,
        ).join_from(
            Org, User, Org.owner_uuid == User.user_uuid, isouter=True
        ).where(and_(
            Org.is_deleted == False,
            *expressions
        ))

        return ORM.pagination(actor.session, stmt, pagination.page_idx,
                              pagination.page_size, [Org.created_at.desc()])

    @staticmethod
    def get_org_detail(actor: Actor, org_uuid: int) -> dict | None:
        stmt = select(
            Org.org_uuid,
            Org.org_name,
            User.user_uuid,
            User.nick_name.label("owner_name"),
            Org.org_remark,
            Org.org_status
        ).join_from(
            Org, User, Org.owner_uuid == User.user_uuid, isouter=True
        ).where(and_(
            Org.is_deleted == False,
            Org.org_uuid == org_uuid
        ))

        return ORM.one(actor.session, stmt)

    @staticmethod
    def check_org_unique(session: Session, org_name: str, except_uuid: str = None) -> APIErrors | None:

        except_expression = None if except_uuid is None else Org.org_uuid != except_uuid

        orm_check_rules = [
            ORMCheckRule(APIErrors.ORG_NAME_ALREADY_EXISTS,
                         Org.org_name == org_name),
        ]

        return ORM.check(session, orm_check_rules, except_expression)

    @staticmethod
    def check_admin_org(session: Session, org_uuid: str) -> bool:
        """是否为管理组织"""
        stmt = select(
            Org.is_admin
        ).where(and_(
            Org.is_deleted == False,
            Org.org_uuid == org_uuid,
            Org.is_admin == True
        ))

        return True if ORM.counts(session, stmt) > 0 else False

    @staticmethod
    def create_org(actor: Actor, data: OrgCreate) -> APIErrors:
        """创建组织"""
        try:
            session = actor.session

            if result := OrgAPI.check_org_unique(session, data.org_name):
                return result

            # 获取owner的详情
            if (owner := UserAPI.get_account_detail(actor, data.owner_uuid)) is None:
                return APIErrors.ORG_OWNER_NOT_AVAIABLE

            # 创建组织信息
            org = Org(org_uuid=generate_uuid_str(), **data.model_dump())

            # 创建组织用户信息
            org_user = OrgUser(
                org_uuid=org.org_uuid,
                user_uuid=org.owner_uuid,
                org_user_name=owner["nick_name"]
            )

            session.add_all([org, org_user])
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR

    @staticmethod
    def update_org(actor: Actor, data: OrgUpdate) -> APIErrors:
        try:
            session = actor.session

            # 平台组织不可操作
            if OrgAPI.check_admin_org(session, data.org_uuid) == True:
                return APIErrors.ORG_ADMIN_CTRL_DINED

            # 获取组织所有者的信息
            stmt = select(OrgUser.id).where(and_(
                OrgUser.user_uuid == data.owner_uuid,
                OrgUser.org_uuid == data.org_uuid
            ))

            # 所有者不是组织用户
            if ORM.counts(session, stmt) == 0:
                stmt = select(User.nick_name).where(and_(
                    User.is_deleted == False,
                    User.status == UserStatus.ENABLE.value,
                    User.user_uuid == data.owner_uuid
                ))

                if user := ORM.one(session, stmt):
                    org_user = OrgUser(org_uuid=data.org_uuid,
                                       user_uuid=data.owner_uuid,
                                       user_name=user["nick_name"]
                                       )
                    session.add(org_user)
                else:
                    return APIErrors.ORG_OWNER_NOT_AVAIABLE

                    # 修改组织信息
            stmt = update(Org).where(Org.org_uuid == data.org_uuid).values(
                org_name=data.org_name,
                owner_uuid=data.owner_uuid,
                remark=data.remark,
                status=data.status
            )

            session.execute(stmt)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR

    @staticmethod
    def delete_org(actor: Actor, data: OrgDelete) -> APIErrors:
        try:
            session = actor.session
            deleted_uuid = data.org_uuid

            if OrgAPI.check_admin_org(session, deleted_uuid) == True:
                return APIErrors.ORG_ADMIN_CTRL_DINED

            # 组织逻辑删除(组织用户信息保留)
            stmt = update(Org).where(Org.org_uuid == deleted_uuid).values(
                is_deleted=True,
                org_name=deleted_uuid
            )

            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR
