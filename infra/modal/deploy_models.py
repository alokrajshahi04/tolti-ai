"""
Modal deployment for TOLTI AI model endpoints.

Deploys two vLLM-backed OpenAI-compatible servers:
- Code model: Qwen/Qwen2.5-Coder-7B-Instruct
- Text model: Qwen/Qwen3-8B (non-thinking mode)

Endpoints are protected by Modal proxy tokens or FastAPI bearer auth.
Revisions must be pinned after smoke tests; do not deploy without approval.
"""

from __future__ import annotations

import asyncio
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
CODE_MODEL_REVISION = os.environ.get("TOLTI_CODE_REVISION", "main")

TEXT_MODEL_ID = "Qwen/Qwen3-8B"
TEXT_MODEL_REVISION = os.environ.get("TOLTI_TEXT_REVISION", "main")

VLLM_PORT = 8000
GPU_TYPE = "L40S"  # 7B-8B class; verify VRAM fit during smoke tests
TENSOR_PARALLEL = 1

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
hf_secret = modal.Secret.from_name("tolti-hf", required=False)
auth_secret = modal.Secret.from_name("tolti-endpoint-auth", required=False)


# ---------------------------------------------------------------------------
# Shared vLLM server class
# ---------------------------------------------------------------------------
@app.server(
    image=vllm_image,
    gpu=GPU_TYPE,
    scaledown_window=15 * 60,
    startup_timeout=10 * 60,
    port=VLLM_PORT,
    routing_region="us-east",
    target_concurrency=8,
    secrets=[hf_secret, auth_secret],
)
class ModelServer:
    """Parametrized vLLM server."""

    model_id: str = modal.parameter()
    model_revision: str = modal.parameter()
    enable_thinking: bool = modal.parameter(default=False)

    @modal.enter()
    def start(self) -> None:
        cmd = [
            "vllm",
            "serve",
            self.model_id,
            "--revision",
            self.model_revision,
            "--served-model-name",
            self.model_id,
            "llm",
            "--host",
            "0.0.0.0",
            "--port",
            str(VLLM_PORT),
            "--uvicorn-log-level=info",
            "--async-scheduling",
            "--tensor-parallel-size",
            str(TENSOR_PARALLEL),
        ]
        if self.enable_thinking:
            cmd += ["--enable-reasoning", "--reasoning-parser", "qwen3"]
        print("STARTING:", " ".join(cmd))
        self.process = subprocess.Popen(cmd)

    @modal.exit()
    def stop(self) -> None:
        if hasattr(self, "process"):
            self.process.terminate()


# ---------------------------------------------------------------------------
# Typed endpoint definitions
# ---------------------------------------------------------------------------
CodeServer = ModelServer(
    model_id=CODE_MODEL_ID,
    model_revision=CODE_MODEL_REVISION,
    enable_thinking=False,
)

TextServer = ModelServer(
    model_id=TEXT_MODEL_ID,
    model_revision=TEXT_MODEL_REVISION,
    enable_thinking=False,
)


# ---------------------------------------------------------------------------
# Smoke-test entrypoint (opt-in, does not deploy automatically)
# ---------------------------------------------------------------------------
@app.local_entrypoint()
async def smoke(
    model: str = "code",
    prompt: str = "Write a Python hello world.",
    timeout: int = 300,
):
    """Run a real inference smoke test against the deployed server.

    Usage:
        modal run infra/modal/deploy_models.py --model code --prompt "Write a sort function"
    """
    import asyncio

    server = CodeServer if model == "code" else TextServer
    url = await server.get_url.aio()
    print(f"Smoke-testing {server.model_id} at {url}")

    async with aiohttp.ClientSession(base_url=url) as session:
        deadline = time.time() + timeout
        while time.time() < deadline:
            async with session.get("/health", timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    break
                if resp.status == 503:
                    await asyncio.sleep(2)
                    continue
                    raise RuntimeError(f"Health failed: HTTP {resp.status}")
        else:
            raise RuntimeError("Health check timed out")

        print("Health OK")
        payload = {
            "model": server.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "max_tokens": 64,
        }
        async with session.post(
            "/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as resp:
            data = await resp.json()
            print("RESULT:", json.dumps(data, indent=2))
