from fastapi import APIRouter, Depends, HTTPException, Query
from api.schema.org import OrgAPI, OrgCreate, OrgUpdate, OrgDelete
from .base import get_actor_info, get_pagination, Rsp

api = APIRouter(prefix="/org")


@api.get("/list", summary="获取组织列表信息")
async def get_org_list(org_name: str = Query(default="", description="组织名"),
                       status: int = Query(default=None, description="组织状态"),
                       pagination=Depends(get_pagination),
                       actor=Depends(get_actor_info)
                       ) -> Rsp:
    try:
        data = OrgAPI.get_org_list(actor, pagination, org_name, status)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get("/detail", summary="获取组织详情信息")
async def get_org_detail(org_uuid: str = Query(description="组织UUID"),
                         actor=Depends(get_actor_info)
                         ) -> Rsp:
    try:
        data = OrgAPI.get_org_detail(actor, org_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.post("/create", summary="创建组织")
async def create_org(data: OrgCreate,
                     actor=Depends(get_actor_info)
                     ) -> Rsp:
    try:
        result = OrgAPI.create_org(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)


@api.post("/update", summary="修改组织")
async def update_org(data: OrgUpdate,
                     actor=Depends(get_actor_info)
                     ) -> Rsp:
    try:
        result = OrgAPI.update_org(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)


@api.post("/delete", summary="删除组织")
async def delete_org(data: OrgDelete,
                     actor=Depends(get_actor_info)
                     ) -> Rsp:
    try:
        result = OrgAPI.delete_org(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result.value)
