from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_session_cookie
from app.core.database import get_session
from app.repositories.memberships import get_membership
from app.repositories.rooms import get_room
from app.services.memberships import grant_role
from app.services.memberships import handoff_driver as handoff_driver_service

router = APIRouter()


class RoleUpdateRequest(BaseModel):
    role: str
    expected_room_revision: int


class HandoffRequest(BaseModel):
    target_principal_id: str
    expected_room_revision: int


@router.post("/rooms/{room_id}/memberships/{principal_id}/role")
def update_member_role(
    room_id: UUID,
    principal_id: UUID,
    request: RoleUpdateRequest,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    room = get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="RESOURCE_NOT_FOUND")
    membership = grant_role(
        db, room_id, principal_id, request.role, session.principal_id
    )
    if not membership:
        raise HTTPException(status_code=403, detail="ROLE_FORBIDDEN")
    room.revision += 1
    db.commit()
    return {
        "principal_id": str(principal_id),
        "role": membership.role,
        "revision": room.revision,
    }


@router.delete("/rooms/{room_id}/memberships/{principal_id}")
def remove_member(
    room_id: UUID,
    principal_id: UUID,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    membership = get_membership(db, room_id, session.principal_id)
    if not membership or not membership.is_host:
        raise HTTPException(status_code=403, detail="ROLE_FORBIDDEN")
    target = get_membership(db, room_id, principal_id)
    if not target:
        raise HTTPException(status_code=404, detail="RESOURCE_NOT_FOUND")
    if target.is_host:
        raise HTTPException(status_code=403, detail="ROLE_FORBIDDEN")
    db.delete(target)
    db.commit()
    return {}


@router.post("/rooms/{room_id}/handoff")
def handoff_driver(
    room_id: UUID,
    request: HandoffRequest,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    room = handoff_driver_service(
        db, room_id, UUID(request.target_principal_id), session.principal_id
    )
    if not room:
        raise HTTPException(status_code=403, detail="ROLE_FORBIDDEN")
    room.revision += 1
    db.commit()
    return {
        "id": str(room.id),
        "driver_principal_id": str(room.driver_principal_id),
        "revision": room.revision,
    }
