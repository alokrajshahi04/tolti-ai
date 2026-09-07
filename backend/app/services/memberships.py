from typing import Optional
from uuid import UUID

from app.core.roles import Role
from app.models import Membership, Room
from app.repositories.events import create_event, get_next_seq
from app.repositories.memberships import (
    get_membership,
    set_driver,
)
from app.repositories.rooms import get_room


def grant_role(
    db,
    room_id: UUID,
    target_principal_id: UUID,
    role: str,
    actor_principal_id: UUID,
) -> Optional[Membership]:
    room = get_room(db, room_id)
    if not room:
        return None
    actor = get_membership(db, room_id, actor_principal_id)
    if not actor or not actor.is_host:
        return None
    membership = get_membership(db, room_id, target_principal_id)
    if not membership:
        return None
    if membership.role == Role.DRIVER and role != Role.DRIVER:
        membership = set_driver(db, room_id, actor_principal_id) or membership
    membership.role = role
    db.flush()
    payload = f'{{"room_id":"{room_id}","principal_id":"{target_principal_id}","role":"{role}"}}'
    seq = get_next_seq(db, room_id)
    create_event(
        db,
        room_id,
        "membership.role_changed",
        payload,
        actor_principal_id=actor_principal_id,
        seq=seq,
    )
    return membership


def handoff_driver(
    db,
    room_id: UUID,
    target_principal_id: UUID,
    actor_principal_id: UUID,
) -> Optional[Room]:
    room = get_room(db, room_id)
    if not room:
        return None
    actor = get_membership(db, room_id, actor_principal_id)
    if not actor or not actor.is_host:
        return None
    target = get_membership(db, room_id, target_principal_id)
    if not target:
        return None
    old_driver_id = room.driver_principal_id
    if old_driver_id == target_principal_id:
        return room
    room.driver_principal_id = target_principal_id
    if target.role != Role.DRIVER:
        target.role = Role.DRIVER
    old_driver = get_membership(db, room_id, old_driver_id)
    if old_driver and old_driver.role == Role.DRIVER:
        old_driver.role = Role.WATCHER
    db.flush()
    payload = (
        f'{{"room_id":"{room_id}","new_driver":"{target_principal_id}",'
        f'"old_driver":"{old_driver_id}"}}'
    )
    seq = get_next_seq(db, room_id)
    create_event(
        db, room_id, "driver.handed_off", payload, actor_principal_id=actor_principal_id, seq=seq
    )
    return room
