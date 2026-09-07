from uuid import UUID

from app.core.roles import Role
from app.repositories.memberships import get_membership


def get_capabilities(db, room_id: UUID, principal_id: UUID) -> dict:
    membership = get_membership(db, room_id, principal_id)
    if not membership:
        return {}
    caps = {
        "can_read": True,
        "can_write": membership.role == Role.DRIVER,
        "can_grant_roles": membership.is_host,
        "role": membership.role,
        "is_host": membership.is_host,
    }
    return caps
