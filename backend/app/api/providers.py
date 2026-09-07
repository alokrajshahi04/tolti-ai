from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_session_cookie
from app.providers.fake import FakeProvider
from app.providers.protocol import ProviderKey
from app.schemas.provider import ProviderHealthResponse
from app.workflows.router import RouterError, TaskIntent, WorkflowRouter

router = APIRouter()

_fake_code = FakeProvider(ProviderKey.CODE, "Qwen/Qwen2.5-Coder-7B-Instruct", "fake-code-rev")
_fake_text = FakeProvider(ProviderKey.TEXT, "Qwen/Qwen3-8B", "fake-text-rev")
_default_router = WorkflowRouter({ProviderKey.CODE: _fake_code, ProviderKey.TEXT: _fake_text})


def get_router() -> WorkflowRouter:
    return _default_router


@router.get("/providers/health")
def provider_health(session=Depends(get_session_cookie)):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    router = get_router()
    items = []
    for provider_key, provider in router.providers.items():
        health = provider.health()
        items.append(ProviderHealthResponse(
            provider_key=provider_key.value,
            configured=health.configured,
            reachable=health.reachable,
            inferred=health.inferred,
            error=health.error,
            model_id=health.model_id,
            model_revision=health.model_revision,
        ))
    return {"items": items}


@router.post("/workflows/route")
def route_workflow(request: TaskIntent, session=Depends(get_session_cookie)):
    if not session:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    router = get_router()
    try:
        decision = router.route(request, session.role, consent=True)
    except RouterError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.code)
    from app.schemas.provider import RouteDecisionResponse
    return RouteDecisionResponse(
        workflow=decision.workflow,
        provider_key=decision.provider_key.value,
        model_id=decision.model_id,
        model_revision=decision.model_revision,
        selected_by=decision.selected_by,
        reason_code=decision.reason_code,
        clarification=decision.clarification,
    )
