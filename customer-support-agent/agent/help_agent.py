"""Strands agent construction and the products MCP connection."""

from __future__ import annotations

from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.anthropic import AnthropicModel
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


def build_model(cfg: Config) -> AnthropicModel:
    if cfg.use_llm_provider:
        # The SDK adds /v1/messages itself, so drop a /v1 the provider URL may already end with.
        base_url = cfg.llm_provider_url.rstrip("/").removesuffix("/v1")
        # The Agent Manager LLM gateway reads its key from API-Key and adds Anthropic's own key
        # upstream. The SDK also sends api_key as x-api-key.
        client_args = {
            "base_url": base_url,
            "api_key": cfg.llm_provider_key,
            "default_headers": {"API-Key": cfg.llm_provider_key},
        }
    else:
        client_args = {"api_key": cfg.anthropic_api_key}
    # No temperature: current Claude models reject sampling parameters.
    return AnthropicModel(client_args=client_args, model_id=cfg.model, max_tokens=cfg.max_tokens)


def build_agent(cfg: Config, tools: list) -> Agent:
    return Agent(
        model=build_model(cfg),
        tools=tools,
        system_prompt=SYSTEM_PROMPT.format(store=cfg.store_name),
        callback_handler=None,
    )
