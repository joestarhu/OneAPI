from fastapi import APIRouter, Depends, Query
from api.api.base import get_page, user_auth
from api.service.org import OrgAPI  # noqa

api = APIRouter(prefix="/org")


@api.get("/list", summary="获取组织信息列表")
def get_list(*, actor=Depends(user_auth), page=Depends(get_page)):
    return OrgAPI.get_list()


@api.get("/detail", summary="获取组织详情")
def get_detail(*, actor=Depends(user_auth), org_id: int = Query(description="组织ID")):
    return OrgAPI.get_detail()


@ api.post("/create", summary="创建组织")
def create_org(*, actor=Depends(user_auth)):
    return OrgAPI.create_org()


@api.post("/update", summary="修改组织")
def update_org(*, actor=Depends(user_auth)):
    return OrgAPI.update_org()


@api.post("/delete", summary="删除组织")
def delete_org(*, actor=Depends(user_auth)):
    return OrgAPI.delete_org()
