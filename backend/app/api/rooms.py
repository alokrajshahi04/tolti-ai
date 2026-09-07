from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_session_cookie
from app.core.database import get_session
from app.repositories.events import get_events_after_seq, get_latest_seq
from app.repositories.memberships import get_membership, list_memberships
from app.repositories.rooms import get_room
from app.repositories.sessions import get_principal
from app.services.authorization import get_capabilities
from app.services.rooms import create_room_service, join_room_by_invite

router = APIRouter()


class CreateRoomRequest(BaseModel):
    name: str


class JoinRoomRequest(BaseModel):
    invite_token: str


@router.post("/rooms", status_code=201)
def create_room_route(
    request: CreateRoomRequest,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    room = create_room_service(db, request.name, session.principal_id)
    db.commit()
    return {
        "id": str(room.id),
        "name": room.name,
        "host_principal_id": str(room.host_principal_id),
        "driver_principal_id": str(room.driver_principal_id),
        "revision": room.revision,
        "last_seq": room.last_seq,
    }


@router.get("/rooms")
def list_rooms(session=Depends(get_session_cookie), db: Session = Depends(get_session)):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    memberships = list_memberships(db, session.principal_id)
    items = []
    for m in memberships:
        room = m.room
        items.append({
            "id": str(room.id),
            "name": room.name,
            "revision": room.revision,
            "host_principal_id": str(room.host_principal_id),
            "driver_principal_id": str(room.driver_principal_id),
            "last_seq": room.last_seq,
            "role": m.role,
            "is_host": m.is_host,
        })
    return {"items": items}


@router.get("/rooms/{room_id}/snapshot")
def get_room_snapshot(
    room_id: UUID,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    room = get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="RESOURCE_NOT_FOUND")
    membership = get_membership(db, room_id, session.principal_id)
    if not membership:
        raise HTTPException(status_code=404, detail="RESOURCE_NOT_FOUND")
    caps = get_capabilities(db, room_id, session.principal_id)
    members = []
    for m in list_memberships(db, room_id):
        principal = get_principal(db, m.principal_id)
        members.append({
            "principal_id": str(m.principal_id),
            "display_name": principal.display_name if principal else "",
            "role": m.role,
            "is_host": m.is_host,
        })
    snapshot_seq = get_latest_seq(db, room_id)
    return {
        "room": {
            "id": str(room.id),
            "name": room.name,
            "host_principal_id": str(room.host_principal_id),
            "driver_principal_id": str(room.driver_principal_id),
            "revision": room.revision,
            "last_seq": room.last_seq,
        },
        "memberships": members,
        "active_run": None,
        "snapshot_seq": snapshot_seq,
        "capabilities": caps,
    }


@router.post("/rooms/join")
def join_room(
    request: JoinRoomRequest,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    try:
        token = bytes.fromhex(request.invite_token)
    except ValueError:
        raise HTTPException(status_code=404, detail="RESOURCE_NOT_FOUND")
    membership = join_room_by_invite(db, token, session.principal_id)
    if not membership:
        raise HTTPException(status_code=404, detail="RESOURCE_NOT_FOUND")
    db.commit()
    return {
        "room_id": str(membership.room_id),
        "principal_id": str(membership.principal_id),
        "role": membership.role,
    }


@router.get("/rooms/{room_id}/events")
def get_room_events(
    room_id: UUID,
    after_seq: int = Query(0),
    limit: int = Query(500),
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    membership = get_membership(db, room_id, session.principal_id)
    if not membership:
        raise HTTPException(status_code=404, detail="RESOURCE_NOT_FOUND")
    events = get_events_after_seq(db, room_id, after_seq, limit)
    items = []
    for e in events:
        items.append({
            "event_id": str(e.id),
            "seq": e.seq,
            "type": e.type,
            "occurred_at": e.occurred_at.isoformat(),
            "payload": e.payload,
        })
    next_after = events[-1].seq if events else after_seq
    has_more = len(events) == limit
    high_water = get_latest_seq(db, room_id)
    return {
        "items": items,
        "next_after_seq": next_after,
        "has_more": has_more,
        "high_water_seq": high_water,
    }
