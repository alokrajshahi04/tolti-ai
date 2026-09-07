from datetime import datetime
from typing import Optional
from uuid import UUID

from app.core.security import hash_token
from app.models import Invite


def create_invite(
    db,
    room_id: UUID,
    token: bytes,
    created_by_principal_id: UUID,
    expires_at: datetime,
) -> Invite:
    invite = Invite(
        room_id=room_id,
        token_hash=hash_token(token),
        created_by_principal_id=created_by_principal_id,
        expires_at=expires_at,
    )
    db.add(invite)
    db.flush()
    return invite


def get_invite_by_token(db, token: bytes) -> Optional[Invite]:
    token_hash = hash_token(token)
    return db.query(Invite).filter(Invite.token_hash == token_hash).first()


def mark_invite_consumed(db, invite_id: UUID, principal_id: UUID) -> None:
    invite = db.query(Invite).filter(Invite.id == invite_id).first()
    if invite and not invite.consumed and not invite.revoked:
        invite.consumed = True
        invite.consumed_by_principal_id = principal_id
        db.flush()


def revoke_invite(db, invite_id: UUID) -> None:
    invite = db.query(Invite).filter(Invite.id == invite_id).first()
    if invite:
        invite.revoked = True
        db.flush()
