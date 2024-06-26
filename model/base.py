from datetime import datetime
from sqlalchemy import create_engine, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped as M, mapped_column as mc, sessionmaker

from api.config.settings import settings  # noqa


engine = create_engine(url=settings.db_rds, echo=False,
                       pool_recycle=settings.pool_recycle_seconds)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class ModelBase(DeclarativeBase):
    """通用字段
    """
    id: M[int] = mc(BigInteger, primary_key=True, comment="ID")
    create_id: M[int] = mc(BigInteger, nullable=True, comment="数据创建者ID")
    update_id: M[int] = mc(BigInteger, nullable=True, comment="数据更新者ID")
    create_dt: M[datetime] = mc(
        DateTime, default=datetime.now(), comment="数据创建时间")
    update_dt: M[datetime] = mc(
        DateTime, default=datetime.now(), comment="数据更新时间")
