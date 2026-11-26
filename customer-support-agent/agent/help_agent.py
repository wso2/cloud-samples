"""Strands agent construction and the products MCP connection."""

from __future__ import annotations

from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import Model
from strands.models.anthropic import AnthropicModel
from strands.models.gemini import GeminiModel
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient

from config import Config

SYSTEM_PROMPT = """You are the customer support agent for {store}, an outdoor gear store.
You help shoppers find products, check stock and sizes, compare items and understand store policies.

- Use the product tools for every fact about a product, its stock, its price or a policy. Never guess.
- Find SKUs with searchProducts before calling the other tools.
- You only answer questions about {store}'s products, stock and policies. Politely decline anything else.
- Never repeat personal details a shopper shares, such as phone numbers, emails or addresses.
- Keep answers short and friendly. Give prices with their currency.
"""


def create_mcp_client(cfg: Config) -> MCPClient:
    headers = {"X-API-Key": cfg.mcp_api_key} if cfg.mcp_api_key else {}
    return MCPClient(lambda: streamablehttp_client(cfg.products_mcp_url, headers=headers))


def build_model(cfg: Config) -> Model:
    if not cfg.use_llm_provider:
        # No temperature: current Claude models reject sampling parameters.
        return AnthropicModel(
            client_args={"api_key": cfg.anthropic_api_key}, model_id=cfg.model, max_tokens=cfg.max_tokens
        )
    # Every call goes to the Agent Management LLM gateway, which reads its key from API-Key and adds
    # the provider's own key upstream. Each SDK also sends the key in its own header, which the
    # gateway replaces.
    url = cfg.llm_provider_url.rstrip("/")
    key = cfg.llm_provider_key
    gateway = {"API-Key": key}
    if cfg.llm_provider == "anthropic":
        # The SDK adds /v1/messages itself, so drop a /v1 the provider URL may already end with.
        client_args = {"base_url": url.removesuffix("/v1"), "api_key": key, "default_headers": gateway}
        return AnthropicModel(client_args=client_args, model_id=cfg.model, max_tokens=cfg.max_tokens)
    if cfg.llm_provider == "openai":
        # Agent Management's OpenAI provider points at https://api.openai.com/v1, so the gateway URL
        # already stands for /v1 and the SDK adds /chat/completions.
        client_args = {"base_url": url, "api_key": key, "default_headers": gateway}
        return OpenAIModel(client_args=client_args, model_id=cfg.model, params={"max_completion_tokens": cfg.max_tokens})
    if cfg.llm_provider == "mistralai":
        # Mistral's chat API is OpenAI-compatible under /v1; its provider points at https://api.mistral.ai.
        client_args = {"base_url": f"{url.removesuffix('/v1')}/v1", "api_key": key, "default_headers": gateway}
        return OpenAIModel(client_args=client_args, model_id=cfg.model, params={"max_tokens": cfg.max_tokens})
    if cfg.llm_provider == "gemini":
        # The Gemini SDK adds /v1beta/models/... to the base URL and sends the key as x-goog-api-key.
        client_args = {"api_key": key, "http_options": {"base_url": url, "headers": gateway}}
        return GeminiModel(client_args=client_args, model_id=cfg.model, params={"max_output_tokens": cfg.max_tokens})
    raise RuntimeError(f"LLM provider '{cfg.llm_provider}' isn't supported by this sample")


def build_agent(cfg: Config, tools: list) -> Agent:
    return Agent(
        model=build_model(cfg),
        tools=tools,
        system_prompt=SYSTEM_PROMPT.format(store=cfg.store_name),
        callback_handler=None,
    )
