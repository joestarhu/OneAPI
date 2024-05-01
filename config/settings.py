
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """App的配置信息
    """

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # FastAPI配置
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    title: str = "One"
    version: str = "1.0.0"

    # CORS配置
    allow_origins: list[str] = ["*"]

    # 安全相关
    default_passwd: str = "default_passwd"
    encrypt_key: str = "encrypt_key"
    hash_key: str = "hash_key"
    jwt_key: str = "jwt_key"
    jwt_expire_min: int = 60*24

    # 数据库,SQL
    db_rds: str = "mysql+pymysql://username:passwd@host:port/database"
    pool_recycle_seconds: int = 3600

    # 钉钉的AK/SK设置
    ding_ak: str = "ding_ak"
    ding_sk: str = "ding_sk"

    @property
    def fastapi_kwargs(self) -> dict:
        return dict(
            docs_url=self.docs_url,
            redoc_url=self.redoc_url,
            title=self.title,
            version=self.version
        )


settings = AppSettings()
