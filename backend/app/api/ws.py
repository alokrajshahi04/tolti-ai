import json
from uuid import UUID

from fastapi import APIRouter, Depends, Query, WebSocket
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from app.api.deps import get_session_cookie
from app.core.database import get_session
from app.repositories.events import get_events_after_seq
from app.repositories.memberships import get_membership

router = APIRouter()


@router.websocket("/ws/v1/rooms/{room_id}")
async def websocket_room_events(
    websocket: WebSocket,
    room_id: str,
    after_seq: int = Query(0),
    db: Session = Depends(get_session),
):
    await websocket.accept()
    try:
        session = await get_session_cookie(websocket)
        if not session:
            await websocket.close(code=4401, reason="SESSION_REQUIRED")
            return
        room_id_uuid = UUID(room_id)
        membership = get_membership(db, room_id_uuid, session.principal_id)
        if not membership:
            await websocket.close(code=4404, reason="RESOURCE_NOT_FOUND")
            return
        events = get_events_after_seq(db, room_id_uuid, after_seq, limit=500)
        for event in events:
            await websocket.send_json({
                "schema_version": 1,
                "type": "event",
                "event_id": str(event.id),
                "room_id": str(event.room_id),
                "seq": event.seq,
                "event_type": event.type,
                "occurred_at": event.occurred_at.isoformat(),
                "actor_principal_id": str(event.actor_principal_id)
                if event.actor_principal_id
                else None,
                "payload": json.loads(event.payload),
            })
        await websocket.send_json({"type": "connection.ready"})
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except Exception:
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
