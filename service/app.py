from fastapi import APIRouter, HTTPException, Depends, Query
from api.schema.app import AppAPI
from .base import Rsp, get_actor_info, get_pagination

api = APIRouter(prefix="/app")


@api.get("/list", summary="获取应用列表")
async def get_list(actor=Depends(get_actor_info),
                   pagination=Depends(get_pagination),
                   app_name: str = Query(default="", description="应用名称"),
                   app_status: int = Query(default=None, description="应用状态")
                   ):
    try:
        data = AppAPI.get_app_list(actor, pagination, app_name, app_status)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get("/service_list", summary="获取应用服务列表")
async def get_service_list(app_id: int = Query(description="应用ID"),
                           actor=Depends(get_actor_info)
                           ):
    try:
        data = AppAPI.get_service_list(actor, app_id)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)
