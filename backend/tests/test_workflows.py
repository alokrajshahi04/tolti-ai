import asyncio

import pytest

from app.providers.fake import FakeProvider
from app.providers.protocol import ProviderKey, ProviderRequest
from app.workflows.router import RouterError, TaskIntent, WorkflowRouter


@pytest.fixture
def router() -> WorkflowRouter:
    return WorkflowRouter(
        {
            ProviderKey.CODE: FakeProvider(
                ProviderKey.CODE,
                "Qwen/Qwen2.5-Coder-7B-Instruct",
                "code-rev-1",
                reachable=True,
            ),
            ProviderKey.TEXT: FakeProvider(
                ProviderKey.TEXT,
                "Qwen/Qwen3-8B",
                "text-rev-1",
                reachable=True,
            ),
        }
    )


def test_explicit_code_generate_routes_to_code(router: WorkflowRouter):
    intent = TaskIntent(workflow="code_generate", instruction="write a sort function")
    decision = asyncio.run(router.route(intent, "driver", consent=True))
    assert decision.provider_key == ProviderKey.CODE
    assert decision.selected_by == "explicit"
    assert decision.reason_code == "explicit_code_generate"


def test_explicit_code_explain_routes_to_code(router: WorkflowRouter):
    intent = TaskIntent(workflow="code_explain", instruction="explain this function")
    decision = asyncio.run(router.route(intent, "driver", consent=True))
    assert decision.provider_key == ProviderKey.CODE
    assert decision.selected_by == "explicit"


def test_explicit_chat_routes_to_text(router: WorkflowRouter):
    intent = TaskIntent(workflow="chat", instruction="hello")
    decision = asyncio.run(router.route(intent, "driver", consent=True))
    assert decision.provider_key == ProviderKey.TEXT
    assert decision.selected_by == "explicit"


def test_auto_clear_intent_code_generate(router: WorkflowRouter):
    intent = TaskIntent(workflow="auto", instruction="write a python sort function")
    decision = asyncio.run(router.route(intent, "driver", consent=True))
    assert decision.workflow == "code_generate"
    assert decision.selected_by == "auto"
    assert decision.reason_code == "clear_auto_intent"


def test_auto_clear_intent_summarise(router: WorkflowRouter):
    intent = TaskIntent(workflow="auto", instruction="summarise this document")
    decision = asyncio.run(router.route(intent, "driver", consent=True))
    assert decision.workflow == "summarise"
    assert decision.selected_by == "auto"


def test_auto_ambiguous_intent_returns_clarification(router: WorkflowRouter):
    intent = TaskIntent(workflow="auto", instruction="write code and summarise it")
    with pytest.raises(RouterError) as exc:
        asyncio.run(router.route(intent, "driver", consent=True))
    assert exc.value.code == "ROUTE_CLARIFICATION_REQUIRED"
    assert exc.value.status_code == 422


def test_auto_no_match_defaults_to_chat(router: WorkflowRouter):
    intent = TaskIntent(workflow="auto", instruction="hello there")
    decision = asyncio.run(router.route(intent, "driver", consent=True))
    assert decision.workflow == "chat"
    assert decision.selected_by == "auto"
    assert decision.reason_code == "auto_default_chat"


def test_auto_requires_consent(router: WorkflowRouter):
    intent = TaskIntent(workflow="auto", instruction="write code")
    with pytest.raises(RouterError) as exc:
        asyncio.run(router.route(intent, "driver", consent=False))
    assert exc.value.code == "CONSENT_REQUIRED"
    assert exc.value.status_code == 422


def test_auto_requires_driver(router: WorkflowRouter):
    intent = TaskIntent(workflow="auto", instruction="write code")
    with pytest.raises(RouterError) as exc:
        asyncio.run(router.route(intent, "reviewer", consent=True))
    assert exc.value.code == "ROLE_FORBIDDEN"
    assert exc.value.status_code == 403


def test_auto_empty_instruction_rejected(router: WorkflowRouter):
    intent = TaskIntent(workflow="auto", instruction="   ")
    with pytest.raises(RouterError) as exc:
        asyncio.run(router.route(intent, "driver", consent=True))
    assert exc.value.code == "INVALID_REQUEST"
    assert exc.value.status_code == 400


def test_auto_long_instruction_rejected():
    with pytest.raises(Exception):
        TaskIntent(workflow="auto", instruction="x" * 8001)


def test_pdf_qa_requires_sources(router: WorkflowRouter):
    intent = TaskIntent(workflow="pdf_qa", instruction="answer from pdf")
    with pytest.raises(RouterError) as exc:
        asyncio.run(router.route(intent, "driver", consent=True))
    assert exc.value.code == "SOURCE_REQUIRED"
    assert exc.value.status_code == 422


def test_unconfigured_provider_returns_503():
    empty_router = WorkflowRouter({})
    intent = TaskIntent(workflow="chat", instruction="hello")
    with pytest.raises(RouterError) as exc:
        asyncio.run(empty_router.route(intent, "driver", consent=True))
    assert exc.value.code == "WORKFLOW_UNAVAILABLE"
    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_fake_provider_stream():
    provider = FakeProvider(
        ProviderKey.TEXT,
        "fake/model",
        "rev-1",
        response_text="hello world",
    )
    chunks = []
    async for chunk in provider.stream(
        ProviderRequest(model_id="fake/model", messages=[], stream=True)
    ):
        chunks.append(chunk)
    assert len(chunks) == 2
    assert chunks[0].delta == "hello "
    assert chunks[1].delta == "world "
    assert chunks[1].finish_reason == "stop"


@pytest.mark.asyncio
async def test_fake_provider_complete():
    provider = FakeProvider(
        ProviderKey.CODE,
        "fake/code",
        "rev-1",
        response_text="print('hi')",
    )
    resp = await provider.complete(
        ProviderRequest(model_id="fake/code", messages=[])
    )
    assert resp.content == "print('hi')"
    assert resp.finish_reason == "stop"
    assert resp.model_id == "fake/code"
    assert resp.model_revision == "rev-1"
