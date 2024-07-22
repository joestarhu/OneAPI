from fastapi import APIRouter
from . import auth, account, org  # noqa

router = APIRouter()

for router_api, tags in [
    (account.api, ["账户服务"]),
    (auth.api, ["认证服务"]),
    (org.api, ["组织服务"]),
]:
    router.include_router(router_api, tags=tags)
