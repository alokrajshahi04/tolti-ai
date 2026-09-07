from datetime import datetime
from typing import Optional
from uuid import UUID

from app.core.security import hash_token
from app.models import Principal, Session


def create_principal(db, display_name: str) -> Principal:
    principal = Principal(display_name=display_name)
    db.add(principal)
    db.flush()
    return principal


def get_principal(db, principal_id: UUID) -> Optional[Principal]:
    return db.query(Principal).filter(Principal.id == principal_id).first()


def create_session(
    db,
    principal_id: UUID,
    session_token: bytes,
    csrf_token: str,
    expires_at: datetime,
) -> Session:
    session = Session(
        principal_id=principal_id,
        session_token_hash=hash_token(session_token),
        csrf_token=csrf_token,
        expires_at=expires_at,
    )
    db.add(session)
    db.flush()
    return session


def get_session_by_token(db, session_token: bytes) -> Optional[Session]:
    token_hash = hash_token(session_token)
    return (
        db.query(Session)
        .filter(
            Session.session_token_hash == token_hash,
            Session.revoked.is_(False),
        )
        .first()
    )


def revoke_session(db, session_id: UUID) -> None:
    session = db.query(Session).filter(Session.id == session_id).first()
    if session:
        session.revoked = True
