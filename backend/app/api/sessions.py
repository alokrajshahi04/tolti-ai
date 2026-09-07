from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from app.api.deps import get_session_cookie
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import make_expiry, random_token
from app.models import Session
from app.repositories.sessions import create_principal, create_session, revoke_session

router = APIRouter()


class CreateSessionRequest(BaseModel):
    display_name: str


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_session_endpoint(request: CreateSessionRequest, response: Response):
    db = SessionLocal()
    try:
        session_token = random_token(32)
        csrf_token = random_token(16).hex()
        expires_at = make_expiry(12)
        principal = create_principal(db, request.display_name)
        session = create_session(db, principal.id, session_token, csrf_token, expires_at)
        db.commit()
        token_hex = session_token.hex()
        response.set_cookie(
            "tolti_session",
            token_hex,
            httponly=True,
            samesite="strict",
            secure=settings.environment != "development",
            max_age=12 * 60 * 60,
            path="/",
        )
        return {
            "session_token": token_hex,
            "session_id": str(session.id),
            "principal_id": str(principal.id),
            "display_name": principal.display_name,
            "expires_at": expires_at.isoformat(),
            "csrf_token": csrf_token,
        }
    finally:
        db.close()


@router.get("/sessions/current")
def get_current_session(session: Optional[Session] = Depends(get_session_cookie)):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    principal = session.principal
    return {
        "session_id": str(session.id),
        "principal_id": str(principal.id),
        "display_name": principal.display_name,
        "expires_at": session.expires_at.isoformat(),
        "csrf_token": session.csrf_token,
    }


@router.delete("/sessions/current")
def delete_current_session(
    response: Response,
    session: Optional[Session] = Depends(get_session_cookie),
    csrf_token: Optional[str] = None,
):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    if csrf_token != session.csrf_token:
        raise HTTPException(status_code=403, detail="CSRF_INVALID")
    db = SessionLocal()
    try:
        revoke_session(db, session.id)
        db.commit()
    finally:
        db.close()
    response.delete_cookie("tolti_session", path="/")
    return Response(status_code=204)
