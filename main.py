from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config.settings import settings
from api.service import router


def init_app() -> FastAPI:
    """初始化应用"""
    app = FastAPI(**settings.fastapi_kwargs)

    app.include_router(router)

    app.add_middleware(
        CORSMiddleware,
        **settings.fastapi_cors_kwargs
    )

    return app


app = init_app()
