from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """API配置文件"""

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # FastAPI配置信息
    docs_url: str = "/docs"
    redoc_url: str = ""
    title: str = "one"
    version: str = "1.0.0"

    swagger_js_url: str = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.52.4/swagger-ui-bundle.js"
    swagger_css_url: str = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.52.4/swagger-ui.css"

    # CORS配置
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]

    # 安全相关
    default_passwd: str = "default_passwd"
    encrypt_key: str = "encrypt_key"
    aes_key_16: str = "0123456789ABCDEF"
    aes_key_32: str = "0123456789ABCDEF0123456789ABCDEF"
    jwt_key: str = "0123456789ABCDEF"
    jwt_expire_min: int = 60*24

    # 数据库,SQL
    db_rds: str = "mysql+pymysql://username:passwd@host:port/database"
    pool_recycle_seconds: int = 3600

    @property
    def fastapi_kwargs(self) -> dict:
        return dict(
            docs_url=self.docs_url,
            redoc_url=self.redoc_url,
            title=self.title,
            version=self.version,
            swagger_js_url=self.swagger_js_url,
            swagger_css_url=self.swagger_css_url
        )

    @property
    def fastapi_cors_kwargs(self) -> dict:
        return dict(
            allow_origins=self.allow_origins,
            allow_credentials=self.allow_credentials,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers
        )


settings = APISettings()
