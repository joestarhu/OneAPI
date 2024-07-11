from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config.settings import settings
from api.api import router


def init_app() -> FastAPI:
    """初始化fastapi
    """
    app = FastAPI(**settings.fastapi_kwargs)

    # CORS跨域
    app.add_middleware(
        CORSMiddleware,
        **settings.fastapi_cors_kwargs
    )

    app.include_router(router)

    return app


app = init_app()
