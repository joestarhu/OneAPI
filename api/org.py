from fastapi import APIRouter, Depends, Query
from api.api.base import get_page, user_auth
from api.service.org import OrgAPI, OrgList, OrgCreate, OrgUpdate, OrgDelete  # noqa

api = APIRouter(prefix="/org")


@api.get("/list", summary="获取组织信息列表")
def get_list(*, actor=Depends(user_auth), page=Depends(get_page),
             name: str = Query(default=None, description="组织名称"),
             status: int = Query(default=None, description="组织状态")
             ):
    data = OrgList(**page, name=name, status=status)
    return OrgAPI.get_list(actor.db, data)


@api.get("/detail", summary="获取组织详情")
def get_detail(*, actor=Depends(user_auth), org_id: int = Query(description="组织ID")):
    return OrgAPI.get_detail(actor.db, org_id)


@ api.post("/create", summary="创建组织")
def create_org(*, actor=Depends(user_auth), data: OrgCreate):
    return OrgAPI.create_org(actor.db, actor.act, data)


@api.post("/update", summary="修改组织")
def update_org(*, actor=Depends(user_auth), data: OrgUpdate):
    return OrgAPI.update_org(actor.db, actor.act, data)


@api.post("/delete", summary="删除组织")
def delete_org(*, actor=Depends(user_auth), data: OrgDelete):
    return OrgAPI.delete_org(actor.db, actor.act, data)
