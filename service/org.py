from fastapi import APIRouter, Depends, HTTPException, Query

from api.schema.org import OrgAPI
from .base import get_actor_info, get_pagination, Rsp


api = APIRouter(prefix="/org")


@api.get("/list")
async def get_org_list(actor=Depends(get_actor_info),
                       pagination=Depends(get_pagination),
                       org_name: str = Query(default="", description="组织名"),
                       status: int = Query(default=None, description="组织状态")
                       ):
    try:
        data = OrgAPI.get_org_list(
            actor.session, org_name, status, pagination.page_idx, pagination.page_size)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get("/detail")
async def get_org_detail(actor=Depends(get_actor_info),
                         org_id: int = Query(description="组织ID")
                         ) -> Rsp:
    try:
        data = OrgAPI.get_org_detail(actor.session, org_id)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)
