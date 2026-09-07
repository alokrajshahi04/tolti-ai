from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.core.security import now_utc
from app.models import IdempotencyRecord


def create_idempotency_record(
    db,
    key: str,
    principal_id: UUID,
    method: str,
    path: str,
    fingerprint: str,
    result_reference: str,
    expires_at: datetime,
) -> IdempotencyRecord:
    record = IdempotencyRecord(
        key=key,
        principal_id=principal_id,
        method=method,
        path=path,
        fingerprint=fingerprint,
        result_reference=result_reference,
        expires_at=expires_at,
    )
    db.add(record)
    db.flush()
    return record


def get_idempotency_record(db, key: str) -> Optional[IdempotencyRecord]:
    return db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).first()


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
