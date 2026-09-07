from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

from app.core.roles import Role
from app.providers.protocol import Provider, ProviderCapability, ProviderKey


class TaskIntent(BaseModel):
    workflow: Literal[
        "auto",
        "code_generate",
        "code_explain",
        "summarise",
        "chat",
        "pdf_qa",
        "inspection_note",
    ]
    instruction: str = Field(min_length=1, max_length=8000)
    source_ids: list[str] = Field(default_factory=list, max_length=3)
    conversation_version_ids: list[str] = Field(default_factory=list)
    language: str | None = None
    enable_thinking: bool = False


class RouteDecision(BaseModel):
    workflow: str
    provider_key: ProviderKey
    model_id: str
    model_revision: str
    selected_by: Literal["explicit", "auto"]
    reason_code: str
    prompt_version: str = "v1"
    clarification: str | None = None


class RouterError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 422):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


AUTO_INTENT_PATTERNS: dict[re.Pattern, tuple[str, ProviderCapability]] = {
    re.compile(
        r"\b(write|generate|implement|create|build)\b.*\b(code|function|class|api|program|script)\b",
        re.I,
    ): ("code_generate", ProviderCapability.CODE_GENERATE),
    re.compile(
        r"\b(explain|understand|refactor|review|debug|fix)\b.*\b(code|function|class|api|program|script)\b",
        re.I,
    ): ("code_explain", ProviderCapability.CODE_EXPLAIN),
    re.compile(
        r"\b(summarise|summarize|summary|brief|overview)\b", re.I
    ): ("summarise", ProviderCapability.SUMMARISE),
    re.compile(
        r"\b(extract|answer|find|locate|what|where|when|why|how)\b.*\b(page|section|document|pdf)\b",
        re.I,
    ): ("pdf_qa", ProviderCapability.PDF_QA),
    re.compile(
        r"\b(inspection|findings|note|report)\b", re.I
    ): ("inspection_note", ProviderCapability.INSPECTION_NOTE),
    re.compile(
        r"\b(chat|talk|discuss|help|question|conversation)\b", re.I
    ): ("chat", ProviderCapability.CHAT),
}


class WorkflowRouter:
    def __init__(self, providers: dict[ProviderKey, Provider]) -> None:
        self.providers = providers

    async def route(self, intent: TaskIntent, member_role: Role, consent: bool) -> RouteDecision:
        if intent.workflow != "auto":
            return await self._explicit_route(intent, member_role)
        return await self._auto_route(intent, member_role, consent)

    async def _explicit_route(self, intent: TaskIntent, member_role: Role) -> RouteDecision:
        workflow = intent.workflow
        if workflow == "code_generate":
            provider_key = ProviderKey.CODE
            model_id, model_revision = await self._resolve_model(provider_key)
            return RouteDecision(
                workflow=workflow,
                provider_key=provider_key,
                model_id=model_id,
                model_revision=model_revision,
                selected_by="explicit",
                reason_code="explicit_code_generate",
            )
        if workflow == "code_explain":
            provider_key = ProviderKey.CODE
            model_id, model_revision = await self._resolve_model(provider_key)
            return RouteDecision(
                workflow=workflow,
                provider_key=provider_key,
                model_id=model_id,
                model_revision=model_revision,
                selected_by="explicit",
                reason_code="explicit_code_explain",
            )
        if workflow == "pdf_qa":
            if not intent.source_ids:
                raise RouterError(
                    "SOURCE_REQUIRED",
                    "PDF Q&A requires selected sources",
                    status_code=422,
                )
            provider_key = ProviderKey.TEXT
            model_id, model_revision = await self._resolve_model(provider_key)
            return RouteDecision(
                workflow=workflow,
                provider_key=provider_key,
                model_id=model_id,
                model_revision=model_revision,
                selected_by="explicit",
                reason_code="explicit_pdf_qa",
            )
        provider_key = ProviderKey.TEXT
        model_id, model_revision = await self._resolve_model(provider_key)
        return RouteDecision(
            workflow=workflow,
            provider_key=provider_key,
            model_id=model_id,
            model_revision=model_revision,
            selected_by="explicit",
            reason_code="explicit_text",
        )

    async def _auto_route(
        self,
        intent: TaskIntent,
        member_role: Role,
        consent: bool,
    ) -> RouteDecision:
        if not consent:
            raise RouterError(
                "CONSENT_REQUIRED",
                "Explicit consent is required before dispatching",
                status_code=422,
            )
        instruction = intent.instruction.strip()
        if not instruction:
            raise RouterError(
                "INVALID_REQUEST",
                "Instruction must not be empty",
                status_code=400,
            )
        if len(instruction) > 8000:
            raise RouterError(
                "INVALID_REQUEST",
                "Instruction exceeds 8,000 character limit",
                status_code=413,
            )
        if member_role != Role.DRIVER:
            raise RouterError(
                "ROLE_FORBIDDEN",
                "Only the driver can start a run",
                status_code=403,
            )
        matches: list[tuple[str, ProviderCapability]] = []
        for pattern, (workflow, capability) in AUTO_INTENT_PATTERNS.items():
            if pattern.search(instruction):
                matches.append((workflow, capability))
        if len(matches) == 1:
            workflow, capability = matches[0]
            return await self._build_auto_decision(
                intent, workflow, capability, "clear_auto_intent"
            )
        if len(matches) > 1:
            raise RouterError(
                "ROUTE_CLARIFICATION_REQUIRED",
                "Ambiguous intent: please select a specific workflow instead of Auto",
                status_code=422,
            )
        provider_key = ProviderKey.TEXT
        model_id, model_revision = await self._resolve_model(provider_key)
        return RouteDecision(
            workflow="chat",
            provider_key=provider_key,
            model_id=model_id,
            model_revision=model_revision,
            selected_by="auto",
            reason_code="auto_default_chat",
        )

    async def _build_auto_decision(
        self,
        intent: TaskIntent,
        workflow: str,
        capability: ProviderCapability,
        reason_code: str,
    ) -> RouteDecision:
        if workflow in ("code_generate", "code_explain"):
            provider_key = ProviderKey.CODE
        else:
            provider_key = ProviderKey.TEXT
        model_id, model_revision = await self._resolve_model(provider_key)
        return RouteDecision(
            workflow=workflow,
            provider_key=provider_key,
            model_id=model_id,
            model_revision=model_revision,
            selected_by="auto",
            reason_code=reason_code,
        )

    async def _resolve_model(self, provider_key: ProviderKey) -> tuple[str, str]:
        provider = self.providers.get(provider_key)
        if provider is None:
            raise RouterError(
                "WORKFLOW_UNAVAILABLE",
                f"Provider {provider_key} is not configured",
                status_code=503,
            )
        health = await provider.health()
        if not health.configured or not health.reachable:
            raise RouterError(
                "PROVIDER_NOT_CONFIGURED",
                f"Provider {provider_key} is not configured or reachable",
                status_code=503,
            )
        if health.model_id is None or health.model_revision is None:
            raise RouterError(
                "PROVIDER_NOT_CONFIGURED",
                "Provider model is not configured",
                status_code=503,
            )
        return health.model_id, health.model_revision
