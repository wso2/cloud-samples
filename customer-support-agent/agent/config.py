"""Agent configuration, read from env at startup."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


def _env(name: str, default: str | None = None) -> str:
    val = os.environ.get(name) or default
    if val is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return val


def _validate_url(name: str, url: str) -> str:
    parsed = urlparse(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError(
            f"{name} must be an HTTP(S) URL without credentials, query, or fragment"
        )
    return url


def _bool(name: str, default: str) -> bool:
    val = _env(name, default).lower()
    if val not in {"true", "false"}:
        raise RuntimeError(f"{name} must be true or false")
    return val == "true"


@dataclass(frozen=True)
class Config:
    products_mcp_url: str
    # Sent as X-API-Key to the MCP gateway.
    mcp_api_key: str
    use_llm_provider: bool
    llm_provider_url: str
    llm_provider_key: str
    anthropic_api_key: str
    model: str
    max_tokens: int
    store_name: str

    @classmethod
    def from_env(cls) -> "Config":
        use_provider = _bool("USE_LLM_PROVIDER", "true")
        max_tokens = _env("MAX_TOKENS", "16000")
        if not max_tokens.isdigit() or int(max_tokens) < 1:
            raise RuntimeError("MAX_TOKENS must be a positive whole number")
        return cls(
            products_mcp_url=_validate_url("PRODUCTS_MCP_URL", _env("PRODUCTS_MCP_URL")),
            mcp_api_key=_env("MCP_API_KEY", ""),
            use_llm_provider=use_provider,
            # Injected by Agent Manager when an Anthropic LLM provider is bound to the agent.
            llm_provider_url=_validate_url("LLM_PROVIDER_URL", _env("LLM_PROVIDER_URL"))
            if use_provider
            else "",
            llm_provider_key=_env("LLM_PROVIDER_KEY") if use_provider else "",
            # Local runs without Agent Manager only.
            anthropic_api_key=_env("ANTHROPIC_API_KEY") if not use_provider else "",
            model=_env("MODEL", "claude-opus-5-5"),
            max_tokens=int(max_tokens),
            store_name=_env("STORE_NAME", "Summit Outdoor"),
        )
