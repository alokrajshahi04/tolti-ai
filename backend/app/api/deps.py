from typing import Optional

from fastapi import Request

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Session
from app.services.auth import authenticate_session


async def get_session_cookie(request: Request) -> Optional[Session]:
    session_token = request.cookies.get("tolti_session")
    if not session_token:
        return None
    try:
        token_bytes = bytes.fromhex(session_token)
    except ValueError:
        return None
    db = SessionLocal()
    try:
        session = authenticate_session(db, token_bytes)
        return session
    finally:
        db.close()


def validate_origin(request: Request) -> bool:
    origin = request.headers.get("origin", "")
    if not origin:
        return True
    allowed = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    if not allowed:
        return True
    return origin in allowed
