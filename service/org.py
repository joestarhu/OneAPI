# from api.schema.org import OrgAPI, OrgCreate, OrgUpdate, OrgDelete
from fastapi import APIRouter, HTTPException, Query, Depends, Security
from api.schema.org import OrgAPI, OrgCreate
from .base import Rsp, get_pagination, get_actor_info

api = APIRouter(prefix="/org")


@api.get("/list", summary="获取组织列表信息")
async def get_org_list(org_name: str = Query(default="", description="组织名称"),
                       org_status: int = Query(
                           default=None, description="组织状态"),
                       pagination=Depends(get_pagination),
                       actor=Security(get_actor_info, scopes=["org:list"])
                       ) -> Rsp:
    try:
        data = OrgAPI.get_org_list(actor, pagination, org_name, org_status)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get("/detail", summary="获取组织详情信息")
async def get_org_detail(org_uuid: str = Query(description="组织UUID"),
                         actor=Security(get_actor_info, scopes=["org:detail"])
                         ) -> Rsp:
    try:
        data = OrgAPI.get_org_detail(actor, org_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.post("/create", summary="创建组织")
async def create_org(data: OrgCreate,
                     actor=Security(get_actor_info, scopes=["org:create"])
                     ) -> Rsp:
    try:
        result = OrgAPI.create_org(actor, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(**result.value)

# @api.post("/update", summary="修改组织")
# async def update_org(data: OrgUpdate,
#                      actor=Security(get_actor_info, scopes=["org:update"])
#                      ) -> Rsp:
#     try:
#         result = OrgAPI.update_org(actor, data)
#     except Exception as e:
#         raise HTTPException(500, f"{e}")
#     return Rsp(**result.value)

# @api.post("/delete", summary="删除组织")
# async def delete_org(data: OrgDelete,
#                      actor=Security(get_actor_info, scopes=["org:delete"])
#                      ) -> Rsp:
#     try:
#         result = OrgAPI.delete_org(actor, data)
#     except Exception as e:
#         raise HTTPException(500, f"{e}")
#     return Rsp(**result.value)
