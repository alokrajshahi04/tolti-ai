from __future__ import annotations

import asyncio
import json
import time
from typing import AsyncIterator

import aiohttp
from aiohttp import ClientTimeout

from app.providers.protocol import (
    Provider,
    ProviderHealth,
    ProviderKey,
    ProviderRequest,
    ProviderResponse,
    StreamChunk,
)


class ModalAdapter(Provider):
    """Modal-backed provider using vLLM OpenAI-compatible endpoints."""

    def __init__(
        self,
        provider_key: ProviderKey,
        model_id: str,
        model_revision: str,
        endpoint_url: str,
        auth_token: str | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.provider_key = provider_key
        self.model_id = model_id
        self.model_revision = model_revision
        self.endpoint_url = endpoint_url.rstrip("/")
        self.auth_token = auth_token
        self.timeout_seconds = timeout_seconds
        self._session: aiohttp.ClientSession | None = None
        self._cancelled: set[str] = set()

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self.timeout_seconds)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def health(self) -> ProviderHealth:
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.endpoint_url}/health",
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    return ProviderHealth(
                        configured=True,
                        reachable=True,
                        inferred=False,
                        model_id=self.model_id,
                        model_revision=self.model_revision,
                    )
                return ProviderHealth(
                    configured=True,
                    reachable=False,
                    inferred=False,
                    error=f"HTTP {resp.status}",
                    model_id=self.model_id,
                    model_revision=self.model_revision,
                )
        except Exception as exc:
            return ProviderHealth(
                configured=True,
                reachable=False,
                inferred=False,
                error=str(exc),
                model_id=self.model_id,
                model_revision=self.model_revision,
            )

    async def complete(self, request: ProviderRequest) -> ProviderResponse:
        session = await self._get_session()
        payload = self._build_payload(request, stream=False)
        try:
            async with session.post(
                f"{self.endpoint_url}/v1/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return ProviderResponse(
                        content="",
                        finish_reason="error",
                        model_id=self.model_id,
                        model_revision=self.model_revision,
                        raw={"error": text, "status": resp.status},
                    )
                data = await resp.json()
                choice = data["choices"][0]
                content = choice["message"].get("content", "")
                finish_reason = choice.get("finish_reason", "stop")
                usage = data.get("usage")
                return ProviderResponse(
                    content=content,
                    finish_reason=finish_reason,
                    usage=usage,
                    model_id=self.model_id,
                    model_revision=self.model_revision,
                    raw=data,
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            return ProviderResponse(
                content="",
                finish_reason="error",
                model_id=self.model_id,
                model_revision=self.model_revision,
                raw={"error": str(exc)},
            )

    async def stream(self, request: ProviderRequest) -> AsyncIterator[StreamChunk]:
        session = await self._get_session()
        payload = self._build_payload(request, stream=True)
        run_id = self._run_id()
        sequence = 0
        try:
            async with session.post(
                f"{self.endpoint_url}/v1/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    yield StreamChunk(
                        delta=f"ERROR: {text}",
                        finish_reason="error",
                        sequence=sequence,
                    )
                    return
                async for raw in resp.content:
                    if run_id in self._cancelled:
                        yield StreamChunk(
                            delta="",
                            finish_reason="cancelled",
                            sequence=sequence,
                        )
                        return
                    line = raw.decode().strip()
                    if not line or not line.startswith("data: "):
                        continue
                    payload_str = line[len("data: ") :]
                    if payload_str == "[DONE]":
                        yield StreamChunk(
                            delta="",
                            finish_reason="stop",
                            sequence=sequence,
                        )
                        return
                    try:
                        chunk = json.loads(payload_str)
                    except json.JSONDecodeError:
                        continue
                    delta = ""
                    if chunk.get("object") == "chat.completion.chunk":
                        choice = chunk["choices"][0]
                        delta = choice["delta"].get("content", "") or ""
                        finish_reason = choice.get("finish_reason")
                    else:
                        finish_reason = None
                    if delta:
                        sequence += 1
                        yield StreamChunk(
                            delta=delta,
                            finish_reason=finish_reason or "",
                            sequence=sequence,
                        )
        except asyncio.CancelledError:
            yield StreamChunk(
                delta="",
                finish_reason="cancelled",
                sequence=sequence,
            )
            raise

    async def cancel(self, run_id: str) -> None:
        self._cancelled.add(run_id)

    def _build_payload(self, request: ProviderRequest, stream: bool) -> dict:
        payload: dict = {
            "model": request.model_id,
            "messages": request.messages,
            "stream": stream,
            "max_tokens": request.max_tokens,
        }
        if self.provider_key == ProviderKey.CODE:
            payload["temperature"] = 0.2
            payload["top_p"] = 0.9
        else:
            payload["temperature"] = request.temperature
            payload["top_p"] = request.top_p
            payload["top_k"] = request.top_k
            payload["min_p"] = request.min_p
        if request.stop:
            payload["stop"] = request.stop
        if self.provider_key == ProviderKey.TEXT and request.enable_thinking:
            payload["chat_template_kwargs"] = {"enable_thinking": True}
        return payload

    def _run_id(self) -> str:
        return f"{self.provider_key}-{time.time_ns()}"
