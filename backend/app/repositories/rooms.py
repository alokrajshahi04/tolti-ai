from typing import Optional
from uuid import UUID

from app.core.roles import Role
from app.models import Membership, Room


def create_room(db, name: str, host_principal_id: UUID) -> Room:
    room = Room(
        name=name,
        host_principal_id=host_principal_id,
        driver_principal_id=host_principal_id,
    )
    db.add(room)
    db.flush()
    membership = Membership(
        room_id=room.id,
        principal_id=host_principal_id,
        role=Role.DRIVER,
        is_host=True,
    )
    db.add(membership)
    db.flush()
    return room


def get_room(db, room_id: UUID) -> Optional[Room]:
    return db.query(Room).filter(Room.id == room_id).first()


def get_driver(db, room_id: UUID) -> Optional[UUID]:
    room = db.query(Room).filter(Room.id == room_id).first()
    if room:
        return room.driver_principal_id
    return None
