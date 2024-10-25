
from sqlalchemy import select, and_
from jhu.orm import ORM
from api.model.role import Role
from .base import Actor, Pagination


class RoleAPI:
    @staticmethod
    def get_role_list(actor: Actor,
                      pagination: Pagination,
                      role_name: str = "",
                      role_status: int = None
                      ):
        """获取系统默认角色信息"""
        expressions = [expression for condition, expression in [
            (role_name, Role.role_name.ilike(f"%{role_name}%")),
            (role_status is not None, Role.role_status == role_status)
        ] if condition]

        stmt = select(
            Role.id,
            Role.role_name,
            Role.role_remark,
            Role.role_status,
            Role.created_at,
            Role.updated_at
        ).where(and_(
            Role.is_deleted == False,
            Role.org_uuid == "",
            *expressions
        ))

        return ORM.pagination(actor.session, stmt, pagination.page_idx,
                              pagination.page_size, [Role.created_at.desc()])

    @staticmethod
    def get_detail(actor: Actor,
                   role_id: int
                   ) -> dict | None:
        """获取角色详情"""
        stmt = select(
            Role.id,
            Role.role_name,
            Role.role_remark,
            Role.role_status
        ).where(and_(
            Role.is_deleted == False,
            Role.org_uuid == "",
            Role.id == role_id
        ))

        return ORM.one(actor.session, stmt)
