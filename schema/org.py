from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from jhu.orm import ORM
from api.model.org import Org
from api.model.user import User
from .base import Pagination, Actor, Rsp
from .errcode import APIErrors


class OrgCreate(BaseModel):
    org_name: str = Field(description="组织名称")


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
    def check_org_unique(session: Session, org_name: str,) -> APIErrors:
        return APIErrors.NO_ERROR
