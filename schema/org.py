from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from jhu.orm import ORM
from api.model.org import Org
from api.model.user import User
from .base import Pagination, Actor


class OrgAPI:
    @staticmethod
    def get_org_list(session: Session, org_name: str = "", status: int = None, page_idx: int = 1, page_size: int = 10):
        expressions = [expression for condition, expression in [
            (org_name, Org.org_name.contains(org_name)),
            (status is not None, Org.status == status),
        ] if condition]

        statement = select(
            Org.org_id,
            Org.org_name,
            Org.owner_id,
            User.nick_name.label("owner_name"),
            Org.remark,
            Org.status,
            Org.create_dt,
            Org.update_dt
        ).join_from(
            Org, User, Org.owner_id == User.user_id, isouter=True
        ).where(and_(Org.deleted == False, *expressions))

        return ORM.pagination(session, statement, page_idx, page_size, [Org.create_dt.desc()])

    @staticmethod
    def get_org_detail(session: Session, org_id: int):
        statement = select(
            Org.org_id,
            Org.org_name,
            Org.owner_id,
            User.nick_name.label("owner_name"),
            Org.remark,
            Org.status
        ).join_from(
            Org, User, Org.owner_id == User.user_id, isouter=True
        ).where(and_(
            Org.deleted == False,
            Org.org_id == org_id
        ))

        return ORM.one(session, statement)
