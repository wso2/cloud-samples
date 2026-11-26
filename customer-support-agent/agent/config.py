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


def _env_any(*names: str, default: str | None = None) -> str:
    for name in names:
        if os.environ.get(name):
            return os.environ[name]
    if default is None:
        raise RuntimeError(f"Missing required env var: {' or '.join(names)}")
    return default


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


# The LLM providers this sample works with, by Agent Management's template name, and the model each
# uses unless MODEL is set. Providers retire models: check these against each provider's model list
# when updating the sample. Azure OpenAI, Azure AI Foundry and AWS Bedrock aren't here: their model
# is the user's own deployment or account-enabled model, so there is no default to use.
DEFAULT_MODELS = {
    "anthropic": "claude-opus-5-5",
    "openai": "gpt-5.6-terra",
    "gemini": "gemini-flash-latest",
    "mistralai": "mistral-large-latest",
}

# Where Agent Management puts the provider's template name: LLM_PROVIDER_PROVIDER for a configuration
# named LLM_PROVIDER (the AI assistant's path, and the console's), LLM_PROVIDER if set by hand.
PROVIDER_ENVS = ("LLM_PROVIDER_PROVIDER", "LLM_PROVIDER")


def _provider() -> str:
    # Without it (an Agent Management release before the variable, or a local run) the provider is
    # Anthropic, as this sample always used.
    name = _env_any(*PROVIDER_ENVS, default="anthropic").strip().lower()
    if name not in DEFAULT_MODELS:
        raise RuntimeError(
            f"LLM provider '{name}' isn't supported by this sample. Bind one of: {', '.join(DEFAULT_MODELS)}"
        )
    return name


@dataclass(frozen=True)
class Config:
    products_mcp_url: str
    # Sent as X-API-Key to the MCP gateway.
    mcp_api_key: str
    use_llm_provider: bool
    # The bound provider's Agent Management template, such as anthropic or openai.
    llm_provider: str
    llm_provider_url: str
    llm_provider_key: str
    anthropic_api_key: str
    model: str
    max_tokens: int
    store_name: str

    @classmethod
    def from_env(cls) -> "Config":
        use_provider = _bool("USE_LLM_PROVIDER", "true")
        # A local run calls Anthropic directly, so its provider is Anthropic.
        provider = _provider() if use_provider else "anthropic"
        max_tokens = _env("MAX_TOKENS", "16000")
        if not max_tokens.isdigit() or int(max_tokens) < 1:
            raise RuntimeError("MAX_TOKENS must be a positive whole number")
        return cls(
            products_mcp_url=_validate_url("PRODUCTS_MCP_URL", _env("PRODUCTS_MCP_URL")),
            mcp_api_key=_env_any("MCP_API_KEY", "PRODUCTS_MCP_API_KEY", default=""),
            use_llm_provider=use_provider,
            llm_provider=provider,
            # Injected by Agent Manager when an LLM provider is bound to the agent.
            llm_provider_url=_validate_url("LLM_PROVIDER_URL", _env("LLM_PROVIDER_URL"))
            if use_provider
            else "",
            llm_provider_key=_env_any("LLM_PROVIDER_KEY", "LLM_PROVIDER_API_KEY") if use_provider else "",
            # Local runs without Agent Manager only.
            anthropic_api_key=_env("ANTHROPIC_API_KEY") if not use_provider else "",
            model=_env("MODEL", DEFAULT_MODELS[provider]),
            max_tokens=int(max_tokens),
            store_name=_env("STORE_NAME", "Summit Outdoor"),
        )
