from typing import Optional
from uuid import UUID

from app.models import Room, RoomEvent


def create_event(
    db,
    room_id: UUID,
    event_type: str,
    payload: str,
    actor_principal_id: Optional[UUID] = None,
    seq: Optional[int] = None,
) -> RoomEvent:
    event = RoomEvent(
        room_id=room_id,
        seq=seq,
        type=event_type,
        actor_principal_id=actor_principal_id,
        payload=payload,
    )
    db.add(event)
    db.flush()
    return event


def get_next_seq(db, room_id: UUID) -> int:
    room = db.query(Room).filter(Room.id == room_id).with_for_update().first()
    if room.last_seq is None:
        room.last_seq = 0
    room.last_seq += 1
    db.flush()
    return room.last_seq


def get_events_after_seq(db, room_id: UUID, after_seq: int, limit: int = 500):
    return (
        db.query(RoomEvent)
        .filter(RoomEvent.room_id == room_id, RoomEvent.seq > after_seq)
        .order_by(RoomEvent.seq.asc())
        .limit(limit)
        .all()
    )


def get_latest_seq(db, room_id: UUID) -> Optional[int]:
    event = (
        db.query(RoomEvent)
        .filter(RoomEvent.room_id == room_id)
        .order_by(RoomEvent.seq.desc())
        .first()
    )
    if event:
        return event.seq
    return None
