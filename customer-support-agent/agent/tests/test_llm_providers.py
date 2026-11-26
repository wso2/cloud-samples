"""Each supported LLM provider, called through a stand-in for the Agent Management LLM gateway.

No real keys or models: the stand-in records each request and answers in the provider's own
streaming format, so these check what the agent sends (path, gateway key, model) and that it reads
the reply. Run from the agent folder with: python -m pytest tests
"""

from __future__ import annotations

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_MODELS, Config  # noqa: E402
from help_agent import build_agent  # noqa: E402

KEY = "gateway-test-key"


def _sse(events: list[tuple[str | None, dict | str]]) -> bytes:
    out = []
    for name, data in events:
        if name:
            out.append(f"event: {name}")
        out.append(f"data: {data if isinstance(data, str) else json.dumps(data)}")
        out.append("")
    return ("\n".join(out) + "\n").encode()


def _anthropic(model: str) -> bytes:
    return _sse([
        ("message_start", {"type": "message_start", "message": {"id": "m1", "type": "message", "role": "assistant", "model": model, "content": [], "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 3, "output_tokens": 0}}}),
        ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}),
        ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello from the store"}}),
        ("content_block_stop", {"type": "content_block_stop", "index": 0}),
        ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 4}}),
        ("message_stop", {"type": "message_stop"}),
    ])


def _openai(model: str) -> bytes:
    chunk = {"id": "c1", "object": "chat.completion.chunk", "created": 0, "model": model}
    return _sse([
        (None, {**chunk, "choices": [{"index": 0, "delta": {"role": "assistant", "content": "Hello from the store"}, "finish_reason": None}]}),
        (None, {**chunk, "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}),
        (None, {**chunk, "choices": [], "usage": {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7}}),
        (None, "[DONE]"),
    ])


def _gemini(model: str) -> bytes:
    return _sse([
        (None, {"candidates": [{"content": {"role": "model", "parts": [{"text": "Hello from the store"}]}, "finishReason": "STOP", "index": 0}],
                "usageMetadata": {"promptTokenCount": 3, "candidatesTokenCount": 4, "totalTokenCount": 7}, "modelVersion": model}),
    ])


class Gateway:
    """Records requests and answers with the stream for the provider the test set."""

    def __init__(self) -> None:
        self.requests: list[dict] = []
        self.reply = b""
        gateway = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                gateway.requests.append({"path": self.path, "headers": {k.lower(): v for k, v in self.headers.items()}, "body": json.loads(body or b"{}")})
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Content-Length", str(len(gateway.reply)))
                self.end_headers()
                self.wfile.write(gateway.reply)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}/llm"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self) -> None:
        self.server.shutdown()


@pytest.fixture()
def gateway():
    g = Gateway()
    yield g
    g.close()


def _env(monkeypatch, gateway: Gateway, provider: str | None, **extra: str) -> Config:
    for name in ("LLM_PROVIDER_PROVIDER", "LLM_PROVIDER", "MODEL", "LLM_PROVIDER_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("PRODUCTS_MCP_URL", "http://127.0.0.1:1/mcp")
    monkeypatch.setenv("USE_LLM_PROVIDER", "true")
    monkeypatch.setenv("LLM_PROVIDER_URL", gateway.url)
    monkeypatch.setenv("LLM_PROVIDER_API_KEY", KEY)
    if provider:
        monkeypatch.setenv("LLM_PROVIDER_PROVIDER", provider)
    for k, v in extra.items():
        monkeypatch.setenv(k, v)
    return Config.from_env()


CASES = [
    ("anthropic", _anthropic, "/llm/v1/messages"),
    ("openai", _openai, "/llm/chat/completions"),
    ("mistralai", _openai, "/llm/v1/chat/completions"),
    ("gemini", _gemini, None),
]


@pytest.mark.parametrize("provider,stream,path", CASES)
def test_each_provider_calls_the_gateway_with_its_key_and_default_model(monkeypatch, gateway, provider, stream, path):
    cfg = _env(monkeypatch, gateway, provider)
    gateway.reply = stream(cfg.model)
    reply = build_agent(cfg, tools=[])("Hi")
    assert "Hello from the store" in str(reply)
    (req,) = gateway.requests
    assert req["headers"]["api-key"] == KEY
    model = DEFAULT_MODELS[provider]
    if provider == "gemini":
        assert req["path"].startswith(f"/llm/v1beta/models/{model}:streamGenerateContent")
    else:
        assert req["path"] == path
        assert req["body"]["model"] == model


def test_model_can_be_set(monkeypatch, gateway):
    cfg = _env(monkeypatch, gateway, "openai", MODEL="my-model")
    gateway.reply = _openai(cfg.model)
    build_agent(cfg, tools=[])("Hi")
    assert gateway.requests[0]["body"]["model"] == "my-model"


def test_without_the_provider_variable_it_is_anthropic(monkeypatch, gateway):
    cfg = _env(monkeypatch, gateway, None)
    assert (cfg.llm_provider, cfg.model) == ("anthropic", DEFAULT_MODELS["anthropic"])


def test_the_provider_name_set_by_hand_is_read_too(monkeypatch, gateway):
    cfg = _env(monkeypatch, gateway, None, LLM_PROVIDER="Gemini")
    assert cfg.llm_provider == "gemini"


def test_an_unsupported_provider_says_which_are_supported(monkeypatch, gateway):
    with pytest.raises(RuntimeError, match="isn't supported by this sample. Bind one of: anthropic, openai, gemini, mistralai"):
        _env(monkeypatch, gateway, "azure-openai")
