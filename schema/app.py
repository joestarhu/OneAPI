from sqlalchemy import select, and_
from jhu.orm import ORM
from api.model.app import App, AppService
from .base import Actor, Pagination


class AppAPI:
    @staticmethod
    def get_app_list(actor: Actor,
                     pagination: Pagination,
                     app_name: str = "",
                     app_status: int = None
                     ) -> list:
        """获取应用列表"""
        expressions = [expression for condition, expression in [
            (app_name, App.app_name.ilike(f"%{app_name}%")),
            (app_status is not None, App.app_status == app_status)
        ] if condition]

        stmt = select(
            App.id,
            App.app_name,
            App.app_remark,
            App.app_status,
            App.created_at,
            App.updated_at
        ).where(and_(App.is_deleted == False,
                     *expressions))

        return ORM.pagination(actor.session, stmt, page_idx=pagination.page_idx,
                              page_size=pagination.page_size, order=[App.updated_at.desc()])

    @staticmethod
    def get_service_list(actor: Actor,
                         pagination: Pagination,
                         app_id: int):
        """获取应用服务"""
        stmt = select(AppService.id,
                      AppService.service_name,
                      AppService.service_tag
                      ).where(and_(
                          AppService.app_id == app_id
                      ))

        return ORM.pagination(actor.session, stmt,
                              page_idx=pagination.page_idx, page_size=pagination.page_size,
                              order=[AppService.service_tag.asc()]
                              )
