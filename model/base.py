from datetime import datetime
from sqlalchemy import func, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped as M, mapped_column as mc


class ModelBase(DeclarativeBase):
    id: M[int] = mc(BigInteger,
                    primary_key=True,
                    autoincrement=True,
                    comment="ID"
                    )

    created_at: M[datetime] = mc(DateTime,
                                 default=func.now(),
                                 comment="创建数据时间"
                                 )

    updated_at: M[datetime] = mc(DateTime,
                                 default=func.now(),
                                 onupdate=func.now(),
                                 comment="更新数据时间"
                                 )

    # created_at: M[datetime] = mc(TIMESTAMP,
    #                              default=func.current_timestamp(),
    #                              comment="创建数据时间"
    #                              )

    # updated_at: M[datetime] = mc(TIMESTAMP,
    #                              default=func.current_timestamp(),
    #                              onupdate=func.current_timestamp(),
    #                              comment=""
    #                              )
