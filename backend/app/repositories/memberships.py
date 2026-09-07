from typing import Optional
from uuid import UUID

from sqlalchemy.orm import joinedload

from app.models import Membership, Room


def get_membership(db, room_id: UUID, principal_id: UUID) -> Optional[Membership]:
    return (
        db.query(Membership)
        .filter(
            Membership.room_id == room_id,
            Membership.principal_id == principal_id,
        )
        .first()
    )


def list_memberships(db, room_id: UUID):
    return (
        db.query(Membership)
        .options(joinedload(Membership.principal))
        .filter(Membership.room_id == room_id)
        .all()
    )


def update_role(db, room_id: UUID, principal_id: UUID, role: str) -> Optional[Membership]:
    membership = get_membership(db, room_id, principal_id)
    if membership:
        membership.role = role
        db.flush()
    return membership


def set_driver(db, room_id: UUID, principal_id: UUID) -> Optional[Room]:
    room = db.query(Room).filter(Room.id == room_id).first()
    if room:
        room.driver_principal_id = principal_id
        db.flush()
    return room


def create_membership(
    db,
    room_id: UUID,
    principal_id: UUID,
    role: str = "watcher",
    is_host: bool = False,
) -> Membership:
    membership = Membership(room_id=room_id, principal_id=principal_id, role=role, is_host=is_host)
    db.add(membership)
    db.flush()
    return membership
