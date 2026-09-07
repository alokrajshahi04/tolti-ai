from __future__ import annotations

import asyncio
from typing import AsyncIterator

from app.providers.protocol import (
    Provider,
    ProviderHealth,
    ProviderKey,
    ProviderRequest,
    ProviderResponse,
    StreamChunk,
)


class FakeProvider(Provider):
    """Deterministic fake provider for tests."""

    def __init__(
        self,
        provider_key: ProviderKey = ProviderKey.TEXT,
        model_id: str = "fake/model",
        model_revision: str = "fake-rev-1",
        response_text: str = "FAKE RESPONSE",
        reachable: bool = True,
    ) -> None:
        self.provider_key = provider_key
        self.model_id = model_id
        self.model_revision = model_revision
        self.response_text = response_text
        self.reachable = reachable

    async def health(self) -> ProviderHealth:
        return ProviderHealth(
            configured=True,
            reachable=self.reachable,
            inferred=False,
            model_id=self.model_id,
            model_revision=self.model_revision,
        )

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        await asyncio.sleep(0)
        return ProviderResponse(
            content=self.response_text,
            finish_reason="stop",
            usage={"prompt_tokens": 1, "completion_tokens": 1},
            model_id=self.model_id,
            model_revision=self.model_revision,
        )

    async def stream(self, request: ProviderRequest) -> AsyncIterator[StreamChunk]:
        words = self.response_text.split(" ")
        for idx, word in enumerate(words):
            await asyncio.sleep(0)
            yield StreamChunk(
                delta=word + " ",
                finish_reason="stop" if idx == len(words) - 1 else None,
                sequence=idx + 1,
            )

    async def cancel(self, run_id: str) -> None:
        return
