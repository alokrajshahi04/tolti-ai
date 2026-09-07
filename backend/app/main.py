from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="TOLTI backend", lifespan=lifespan)
app.include_router(router, prefix="/api/v1")
