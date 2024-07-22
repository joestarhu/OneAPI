from datetime import datetime
from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped as M, mapped_column as mc


class ModelBase(DeclarativeBase):
    id: M[int] = mc(BigInteger, primary_key=True, comment="ID")
    create_dt: M[datetime] = mc(DateTime, comment="数据创建时间")
    update_dt: M[datetime] = mc(DateTime, comment="数据更新时间")
    create_id: M[int] = mc(BigInteger, nullable=True, comment="数据创建者账户ID")
    update_id: M[int] = mc(BigInteger, nullable=True, comment="数据更新者账户ID")
