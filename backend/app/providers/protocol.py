from abc import ABC, abstractmethod
from enum import StrEnum
from typing import AsyncIterator

from pydantic import BaseModel


class ProviderKey(StrEnum):
    CODE = "code"
    TEXT = "text"


class ProviderCapability(StrEnum):
    CODE_GENERATE = "code_generate"
    CODE_EXPLAIN = "code_explain"
    SUMMARISE = "summarise"
    CHAT = "chat"
    PDF_QA = "pdf_qa"
    INSPECTION_NOTE = "inspection_note"


class ProviderHealth(BaseModel):
    configured: bool
    reachable: bool
    inferred: bool | None = None
    error: str | None = None
    model_id: str | None = None
    model_revision: str | None = None


class StreamChunk(BaseModel):
    delta: str
    finish_reason: str | None
    sequence: int


class ProviderRequest(BaseModel):
    model_id: str
    messages: list[dict]
    stream: bool = False
    max_tokens: int = 1500
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 20
    min_p: float = 0.0
    enable_thinking: bool = False
    stop: list[str] | None = None


class ProviderResponse(BaseModel):
    content: str
    finish_reason: str
    usage: dict | None = None
    model_id: str
    model_revision: str
    raw: dict | None = None


class Provider(ABC):
    @abstractmethod
    async def health(self) -> ProviderHealth:
        """Return provider/model health without producing inference."""
        ...

    @abstractmethod
    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        """Synchronous completion."""
        ...

    @abstractmethod
    async def stream(self, request: ProviderRequest) -> AsyncIterator[StreamChunk]:
        """Stream completion chunks."""
        ...

    @abstractmethod
    async def cancel(self, run_id: str) -> None:
        """Best-effort cancellation of an in-flight request."""
        ...
