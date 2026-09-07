"""
Modal deployment for TOLTI AI model endpoints.

Deploys two vLLM-backed OpenAI-compatible servers:
- Code model: Qwen/Qwen2.5-Coder-7B-Instruct
- Text model: Qwen/Qwen3-8B (non-thinking mode)

Endpoints are protected by Modal proxy auth.
Revisions must be pinned after smoke tests; do not deploy without approval.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Any

import aiohttp
import modal

app = modal.App("tolti-models")

# ---------------------------------------------------------------------------
# Configuration — pin these after smoke tests, do not leave floating
# ---------------------------------------------------------------------------
CODE_MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
CODE_MODEL_REVISION = os.environ.get("TOLTI_CODE_REVISION", "c03e6d358207e414f1eca0bb1891e29f1db0e242")

TEXT_MODEL_ID = "Qwen/Qwen3-8B"
TEXT_MODEL_REVISION = os.environ.get("TOLTI_TEXT_REVISION", "b968826d9c46dd6066d109eabc6255188de91218")

VLLM_PORT = 8000
GPU_TYPE = "L40S"
TENSOR_PARALLEL = 1
IDLE_TIMEOUT = 30 * 60  # 30 minutes

# ---------------------------------------------------------------------------
# Container image
# ---------------------------------------------------------------------------
vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.21.0")
    .env(
        {
            "HF_XET_HIGH_PERFORMANCE": "1",
            "VLLM_LOG_STATS_INTERVAL": "1",
        }
    )
)

# ---------------------------------------------------------------------------
# Secrets — never hard-code tokens
# ---------------------------------------------------------------------------
hf_secret = modal.Secret.from_name("tolti-hf")
auth_secret = modal.Secret.from_name("tolti-endpoint-auth")


# ---------------------------------------------------------------------------
# Code model server
# ---------------------------------------------------------------------------
@app.function(
    image=vllm_image,
    gpu=GPU_TYPE,
    scaledown_window=IDLE_TIMEOUT,
    startup_timeout=10 * 60,
    secrets=[hf_secret, auth_secret],
)
@modal.web_server(
    port=VLLM_PORT,
    startup_timeout=10 * 60,
    requires_proxy_auth=True,
)
def code_server() -> None:
    """Serve Qwen2.5-Coder-7B-Instruct."""
    cmd = [
        "vllm", "serve",
        CODE_MODEL_ID,
        "--revision", CODE_MODEL_REVISION,
        "--served-model-name", CODE_MODEL_ID,
        "llm",
        "--host", "0.0.0.0",
        "--port", str(VLLM_PORT),
        "--uvicorn-log-level=info",
        "--async-scheduling",
        "--tensor-parallel-size", str(TENSOR_PARALLEL),
    ]
    print("STARTING CODE:", " ".join(cmd))
    subprocess.Popen(cmd)


# ---------------------------------------------------------------------------
# Text model server
# ---------------------------------------------------------------------------
@app.function(
    image=vllm_image,
    gpu=GPU_TYPE,
    scaledown_window=IDLE_TIMEOUT,
    startup_timeout=10 * 60,
    secrets=[hf_secret, auth_secret],
)
@modal.web_server(
    port=VLLM_PORT,
    startup_timeout=10 * 60,
    requires_proxy_auth=True,
)
def text_server() -> None:
    """Serve Qwen3-8B (non-thinking mode)."""
    cmd = [
        "vllm", "serve",
        TEXT_MODEL_ID,
        "--revision", TEXT_MODEL_REVISION,
        "--served-model-name", TEXT_MODEL_ID,
        "llm",
        "--host", "0.0.0.0",
        "--port", str(VLLM_PORT),
        "--uvicorn-log-level=info",
        "--async-scheduling",
        "--tensor-parallel-size", str(TENSOR_PARALLEL),
    ]
    print("STARTING TEXT:", " ".join(cmd))
    subprocess.Popen(cmd)


# ---------------------------------------------------------------------------
# Smoke-test entrypoint (opt-in, does not deploy automatically)
# ---------------------------------------------------------------------------
@app.local_entrypoint()
async def smoke(
    model: str = "code",
    prompt: str = "Write a Python hello world.",
    timeout: int = 600,
):
    """Run a real inference smoke test against the deployed server.

    Usage:
        modal run deploy_models.py --model code --prompt "Write a sort function"
    """
    import asyncio

    if model not in {"code", "text"}:
        raise ValueError("model must be 'code' or 'text'")

    server = code_server if model == "code" else text_server
    url = await server.get_web_url.aio()
    print(f"Smoke-testing {model} model at {url}")

    headers = {
        "Modal-Key": os.environ["TOLTI_MODAL_PROXY_KEY"],
        "Modal-Secret": os.environ["TOLTI_MODAL_PROXY_SECRET"],
    }

    async with aiohttp.ClientSession(base_url=url, headers=headers) as session:
        deadline = time.time() + timeout
        last_status = None
        while time.time() < deadline:
            try:
                async with session.get("/health", timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    last_status = resp.status
                    if resp.status == 200:
                        break
                    if resp.status == 503:
                        await asyncio.sleep(2)
                        continue
                    raise RuntimeError(f"Health failed: HTTP {resp.status}")
            except aiohttp.ClientResponseError as exc:
                raise RuntimeError(f"Health request failed: HTTP {exc.status} {exc.message}") from exc
            except Exception as exc:
                print(f"Health check attempt failed: {exc}")
                await asyncio.sleep(2)
        else:
            raise RuntimeError(f"Health check timed out, last status={last_status}")

        print("Health OK")
        payload = {
            "model": CODE_MODEL_ID if model == "code" else TEXT_MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "max_tokens": 64,
        }
        if model == "text":
            payload["chat_template_kwargs"] = {"enable_thinking": False}

        async with session.post(
            "/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"Inference failed: HTTP {resp.status} {text}")
            data = json.loads(text)
            print("RESULT:", json.dumps(data, indent=2))
