from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config.settings import settings  # noqa
from api.api import router


def init_app() -> FastAPI:
    """初始化fastapi
    """
    app = FastAPI(**settings.fastapi_kwargs)

    # CORS跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    return app


app = init_app()
