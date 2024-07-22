from fastapi import APIRouter, Depends, HTTPException

from jhu.orm import ORM
from sqlalchemy import select, and_
from api.model.user import User
from api.model.org import Org, OrgUser
from .deps import get_page, get_actor, Rsp, http_wrapper
api = APIRouter(prefix="/org")


@api.get("/list")
async def get_org_list(org_name: str = "", status: int = None, page=Depends(get_page), act=Depends(get_actor)) -> Rsp:
    try:
        expressions = [expression for condition, expression in [
            (org_name, Org.org_name.contains(org_name)),
            (status is not None, Org.status == status)
        ] if condition]

        stmt = select(
            Org.id,
            Org.org_name,
            User.nick_name.label("owner_name"),
            Org.remark,
            Org.status,
            Org.owner_id,
            Org.create_dt,
            Org.update_dt
        ).join_from(
            Org, User, Org.owner_id == User.id, isouter=True
        ).where(
            and_(Org.deleted == False, *expressions)
        )

        result = ORM.pagination(act.db, stmt, page_idx=page["page_idx"],
                                page_size=page["page_size"], order=[Org.create_dt.desc()])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return Rsp(data=result)


@api.get("/detail")
async def get_org_detail(org_id: int, act=Depends(get_actor)) -> Rsp:
    try:
        stmt = select(
            Org.id,
            Org.owner_id,
            Org.org_name,
            Org.remark,
            Org.status
        ).where(
            and_(Org.deleted == False, Org.id == org_id)
        )

        result = ORM.one(act.db, stmt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return Rsp(data=result)
