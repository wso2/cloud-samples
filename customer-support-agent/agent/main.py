import os

# Set before importing Strands: without it, tool input/output never reach span attributes.
os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental")

import logging
import threading
import uuid
from collections import OrderedDict
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from strands import Agent
import uvicorn

load_dotenv()

from config import Config
from help_agent import build_agent, create_mcp_client

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("customer-support-agent")

CONFIG = Config.from_env()

# Demo-grade memory: keyed on the caller-supplied session_id and lost on restart.
MAX_SESSIONS = 500
SESSIONS: "OrderedDict[str, Agent]" = OrderedDict()
_lock = threading.Lock()

# The MCP connection has its own lock, so connecting never blocks chats that already have an agent.
_mcp_lock = threading.Lock()
_mcp_client = None
_tools: list | None = None


def _product_tools() -> list:
    """Connect to the products MCP server on first use, so the agent can start before it."""
    global _mcp_client, _tools
    if _mcp_client is not None and not _session_alive(_mcp_client):
        # A failed tool call doesn't raise in Strands, so check the session itself before each chat.
        log.warning("products MCP session ended; reconnecting")
        _reset_mcp()
    with _mcp_lock:
        if _tools is None:
            client = create_mcp_client(CONFIG)
            client.start()
            try:
                tools = client.list_tools_sync()
            except Exception:
                client.stop(None, None, None)
                raise
            _mcp_client, _tools = client, tools
            log.info("connected to products MCP server, tools: %s", sorted(t.tool_name for t in tools))
        return _tools


def _session_alive(client) -> bool:
    # strands-agents 1.58 has no public liveness check; treat the client as alive if that changes.
    check = getattr(client, "_is_session_active", None)
    return check() if callable(check) else True


def _reset_mcp() -> None:
    """Drop the MCP connection and the agents bound to its tools, so the next chat reconnects."""
    global _mcp_client, _tools
    with _mcp_lock:
        client, _mcp_client, _tools = _mcp_client, None, None
    with _lock:
        SESSIONS.clear()
    if client is not None:
        try:
            client.stop(None, None, None)
        except Exception:
            log.warning("could not stop the old MCP client", exc_info=True)


@asynccontextmanager
async def lifespan(app):
    yield
    if _mcp_client is not None:
        _mcp_client.stop(None, None, None)


app = FastAPI(title="Customer Support Agent", version="0.1.0", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str = Field(max_length=4000)
    session_id: str | None = Field(default=None, max_length=128)
    # Agent Manager's chat interface sends it; this agent does not use it.
    context: dict | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


def _agent_for(session_id: str) -> Agent:
    # Connect before taking the sessions lock, so a slow MCP connect doesn't block other sessions.
    tools = _product_tools()
    # The sync endpoint runs on a threadpool, so lookup, insert and eviction share one lock.
    with _lock:
        agent = SESSIONS.get(session_id)
        if agent is None:
            agent = build_agent(CONFIG, tools)
            SESSIONS[session_id] = agent
            while len(SESSIONS) > MAX_SESSIONS:
                SESSIONS.popitem(last=False)
        else:
            SESSIONS.move_to_end(session_id)
        return agent


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")

    session_id = req.session_id or str(uuid.uuid4())

    try:
        agent = _agent_for(session_id)
    except Exception as exc:
        log.exception("products MCP server unavailable")
        raise HTTPException(status_code=503, detail="product catalog unavailable") from exc

    try:
        result = agent(req.message)
    except Exception as exc:
        # Upstream errors can carry gateway URLs and provider payloads, so log, do not return.
        log.exception("agent invocation failed", extra={"session_id": session_id})
        # The MCP connection may have died (a restarted server or gateway). Reconnect on the next chat
        # rather than failing every chat until the agent restarts.
        _reset_mcp()
        raise HTTPException(status_code=500, detail="agent invocation failed") from exc

    return ChatResponse(response=str(result), session_id=session_id)


if __name__ == "__main__":
    # Agent Manager starts the agent with `python main.py`.
    uvicorn.run(app, host="0.0.0.0", port=8000)
