from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from jhu.orm import ORM, ORMCheckRule
from api.model.org import Org, OrgUser, OrgStatus
from api.model.user import User
from api.config.security import generate_uuid_str
from .account import AccountAPI
from .base import Pagination, Actor, Rsp
from .errcode import APIErrors


class OrgCreate(BaseModel):
    org_name: str = Field(description="组织名称")
    owner_uuid: str = Field(description="组织所有者UUID")
    remark: str = Field(description="组织备注")
    status: int = Field(default=OrgStatus.ENABLE.value, description="组织状态")


class OrgAPI:
    @staticmethod
    def get_org_list(actor: Actor, pagination: Pagination, org_name: str = "",  status: int = None):
        expressionss = [expression for condition, expression in [
            (org_name, Org.org_name.contains(org_name)),
            (status is not None, Org.status == status),
        ] if condition]

        stmt = select(
            Org.org_uuid,
            Org.org_name,
            User.nick_name.label("owner_name"),
            Org.status,
            Org.remark,
            Org.created_at,
            Org.updated_at,
        ).join_from(
            Org, User, Org.owner_uuid == User.user_uuid, isouter=True
        ).where(and_(
            Org.is_deleted == False,
            *expressionss
        ))

        return ORM.pagination(actor.session, stmt, pagination.page_idx,
                              pagination.page_size, [Org.created_at.desc()])

    @staticmethod
    def get_org_detail(actor: Actor, org_uuid: int):
        stmt = select(
            Org.org_uuid,
            Org.org_name,
            User.user_uuid,
            User.nick_name.label("owner_name"),
            Org.remark,
            Org.status
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
    def create_org(actor: Actor, data: OrgCreate) -> APIErrors:
        try:
            session = actor.session

            if result := OrgAPI.check_org_unique(session, data.org_name):
                return result

            # 判断owner是否有效
            user = AccountAPI.get_account_detail(actor, data.owner_uuid)
            if user is None:
                return APIErrors.OWNER_NOT_EXISTS

            org = Org(org_uuid=generate_uuid_str(),
                      **data.model_dump()
                      )

            org_user = OrgUser(
                org_uuid=org.org_uuid,
                user_uuid=org.owner_uuid,
                user_name=user["nick_name"]
            )

            session.add_all([org, org_user])
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErrors.NO_ERROR
