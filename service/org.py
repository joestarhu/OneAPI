from pydantic import BaseModel, Field
from sqlalchemy import and_, select, update
from sqlalchemy.orm.session import Session
from api.config.security import FieldSecurity, hash_api  # noqa
from api.config.settings import settings  # noqa
from api.model.user import User, UserAuth, UserSettings  # noqa
from api.model.org import OrgSettings, Org, OrgUser  # noqa
from api.service.base import ORM, Rsp, RspError, Pagination, ActInfo  # noqa


class OrgAPI:
    @staticmethod
    def unique_chk(db: Session, account: str, phone_enc: str, except_id: int = None) -> Rsp | None:
        ...

    @staticmethod
    def get_list():
        ...

    @staticmethod
    def get_detail():
        ...

    @staticmethod
    def create_org():
        ...

    @staticmethod
    def update_org():
        ...

    @staticmethod
    def delete_org():
        ...
