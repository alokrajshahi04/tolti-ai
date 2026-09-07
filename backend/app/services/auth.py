from datetime import timedelta
from typing import Optional
from uuid import UUID

from app.core.security import make_expiry, now_utc, random_token
from app.models import Principal, Session
from app.repositories.idempotency import create_idempotency_record, get_idempotency_record
from app.repositories.sessions import (
    create_principal,
    create_session,
    get_session_by_token,
    revoke_session,
)


def create_or_refresh_session(db, display_name: str) -> tuple[Session, Principal]:
    principal = create_principal(db, display_name)
    session_token = random_token(32)
    csrf_token = random_token(16).hex()
    expires_at = make_expiry(12)
    session = create_session(db, principal.id, session_token, csrf_token, expires_at)
    return session, principal


def authenticate_session(db, session_token: bytes) -> Optional[Session]:
    session = get_session_by_token(db, session_token)
    if not session:
        return None
    now = now_utc()
    if session.expires_at < now:
        return None
    if session.revoked:
        return None
    session.last_used_at = now
    db.flush()
    return session


def revoke_current_session(db, session_id: UUID) -> None:
    revoke_session(db, session_id)


def check_idempotency(db, key: str, method: str, path: str, fingerprint: str) -> Optional[str]:
    record = get_idempotency_record(db, key)
    if (
        record
        and record.method == method
        and record.path == path
        and record.fingerprint == fingerprint
    ):
        return record.result_reference
    return None


def record_idempotency(
    db,
    key: str,
    principal_id: UUID,
    method: str,
    path: str,
    fingerprint: str,
    result_reference: str,
) -> None:
    expires_at = now_utc() + timedelta(hours=24)
    create_idempotency_record(
        db, key, principal_id, method, path, fingerprint, result_reference, expires_at
    )
