from fastapi import APIRouter, HTTPException, Depends, Query
from api.schema.role import RoleAPI
from .base import Rsp, get_actor_info, get_pagination

api = APIRouter(prefix="/role")


@api.get("/list", summary="获取角色列表信息")
async def get_list(role_name: str = Query(default="", description="角色名称"),
                   role_status: int = Query(default=None, description="角色状态"),
                   actor=Depends(get_actor_info),
                   pagination=Depends(get_pagination)
                   ) -> Rsp:
    try:
        role_list = RoleAPI.get_role_list(
            actor, pagination, role_name, role_status)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=role_list)


@api.get("/detail", summary="获取角色详情")
async def get_detail(role_id: int = Query(description="角色ID"),
                     actor=Depends(get_actor_info)
                     ) -> Rsp:
    try:
        role = RoleAPI.get_detail(actor, role_id)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=role)
