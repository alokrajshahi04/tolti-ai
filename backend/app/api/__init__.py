from fastapi import APIRouter

from .health import router as health_router
from .invites import router as invites_router
from .memberships import router as memberships_router
from .providers import router as providers_router
from .rooms import router as rooms_router
from .sessions import router as sessions_router
from .ws import router as ws_router

router = APIRouter()
router.include_router(health_router)
router.include_router(rooms_router)
router.include_router(sessions_router)
router.include_router(invites_router)
router.include_router(memberships_router)
router.include_router(providers_router)
router.include_router(ws_router)
