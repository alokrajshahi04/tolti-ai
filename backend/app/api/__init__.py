from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_session
from ..schemas.room import RoomShell

router = APIRouter()


@router.get("/health/live")
def health_live() -> dict:
    return {"status": "ok"}


@router.get("/health/ready")
def health_ready() -> dict:
    return {"status": "ready"}


@router.get("/rooms/{room_id}/shell", response_model=RoomShell)
def get_room_shell(room_id: str, db: Session = Depends(get_session)) -> RoomShell:
    return RoomShell(id=room_id, status="ok")
