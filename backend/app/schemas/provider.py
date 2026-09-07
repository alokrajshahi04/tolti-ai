from pydantic import BaseModel


class ProviderHealthResponse(BaseModel):
    provider_key: str
    configured: bool
    reachable: bool
    inferred: bool | None = None
    error: str | None = None
    model_id: str | None = None
    model_revision: str | None = None


class ProviderCompletionRequest(BaseModel):
    model_id: str
    messages: list[dict]
    stream: bool = False
    max_tokens: int = 1500
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 20
    min_p: float = 0.0
    enable_thinking: bool = False


class ProviderCompletionResponse(BaseModel):
    content: str
    finish_reason: str
    usage: dict | None = None
    model_id: str
    model_revision: str


class TaskIntentRequest(BaseModel):
    workflow: str
    instruction: str
    source_ids: list[str] = []
    conversation_version_ids: list[str] = []
    language: str | None = None
    enable_thinking: bool = False


class RouteDecisionResponse(BaseModel):
    workflow: str
    provider_key: str
    model_id: str
    model_revision: str
    selected_by: str
    reason_code: str
    clarification: str | None = None
