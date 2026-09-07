from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_session_cookie
from app.core.database import get_session
from app.repositories.invites import revoke_invite as revoke_invite_repo
from app.repositories.memberships import get_membership
from app.repositories.rooms import get_room

router = APIRouter()


class InviteCreateRequest(BaseModel):
    expires_in_seconds: int = 1800


@router.post("/rooms/{room_id}/invites")
def create_invite(
    room_id: UUID,
    request: InviteCreateRequest | None = None,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    room = get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="RESOURCE_NOT_FOUND")
    membership = get_membership(db, room_id, session.principal_id)
    if not membership or not membership.is_host:
        raise HTTPException(status_code=403, detail="ROLE_FORBIDDEN")
    from app.core.security import make_expiry, random_token
    from app.repositories.invites import create_invite
    if request is None:
        request = InviteCreateRequest()
    token = random_token(32)
    expires_at = make_expiry(request.expires_in_seconds / 3600)
    invite = create_invite(db, room_id, token, session.principal_id, expires_at)
    db.commit()
    return {
        "invite_id": str(invite.id),
        "token": token.hex(),
        "expires_at": expires_at.isoformat(),
    }


@router.get("/rooms/{room_id}/invites")
def list_invites(
    room_id: UUID,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    membership = get_membership(db, room_id, session.principal_id)
    if not membership or not membership.is_host:
        raise HTTPException(status_code=403, detail="ROLE_FORBIDDEN")
    from app.models import Invite
    invites = db.query(Invite).filter(Invite.room_id == room_id).all()
    items = []
    for inv in invites:
        items.append({
            "invite_id": str(inv.id),
            "expires_at": inv.expires_at.isoformat(),
            "consumed": inv.consumed,
            "revoked": inv.revoked,
        })
    return {"items": items}


@router.delete("/rooms/{room_id}/invites/{invite_id}")
def revoke_invite(
    room_id: UUID,
    invite_id: UUID,
    session=Depends(get_session_cookie),
    db: Session = Depends(get_session),
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    membership = get_membership(db, room_id, session.principal_id)
    if not membership or not membership.is_host:
        raise HTTPException(status_code=403, detail="ROLE_FORBIDDEN")
    revoke_invite_repo(db, invite_id)
    db.commit()
    return {}
