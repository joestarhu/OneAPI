from datetime import datetime
from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped as M, mapped_column as mc


class ModelBase(DeclarativeBase):
    create_id: M[int] = mc(BigInteger, nullable=True, comment="创建数据的用户ID")
    update_id: M[int] = mc(BigInteger, nullable=True, comment="更新数据的用户ID")
    create_dt: M[datetime] = mc(DateTime, comment="创建数据的时间")
    update_dt: M[datetime] = mc(DateTime, comment="更新数据的时间")
