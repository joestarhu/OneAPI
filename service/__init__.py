from fastapi import APIRouter
from . import auth, account, org

router = APIRouter()


services_router = [
    (auth.api, ["认证服务"]),
    (account.api, ["认证服务"]),
    (org.api, ["组织服务"]),
]


for api, tags in services_router:
    router.include_router(api, tags=tags)
