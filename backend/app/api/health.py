from fastapi import APIRouter

router = APIRouter()


@router.get("/health/live")
def health_live() -> dict:
    return {"status": "ok"}


@router.get("/health/ready")
def health_ready() -> dict:
    return {"status": "ready"}
