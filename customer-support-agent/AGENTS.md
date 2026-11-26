# Customer Support Agent

A support agent for Summit Outdoor, a fictional outdoor gear store. Users ask about products, stock and store policies, and the agent answers with live product data through MCP tools. All data is read-only mock data.

Three components run in one project:

```
Customer Support Agent (Agent Management) ──▶ gateway (MCP proxy) ──▶ products-mcp (Integration) ──▶ products-api (Integration)
```

## Deploy on Choreo Cloud

Deploy all three into the project that the user selected, to the Development environment. Repository: `https://github.com/wso2/cloud-samples`, branch `master`. The sample is in the `customer-support-agent` folder, so every path below starts with it. Use these values as they are. Don't ask the user for the repository, the branch or a folder.

### First, tell the user what you build

Before any platform call, say only this, with the project name filled in. Don't add to it, and don't say a plan after it.

> I'll deploy the Customer Support Agent to **{project}**. It answers questions about products, stock and store policies with live data, and is ready in about 15 minutes.
>
> - **Customer Support Agent**: the AI agent you chat with.
> - **Products MCP server**: the tools the agent uses to look up products and stock.
> - **Products API**: the store data behind those tools.

Then show the architecture diagram (`docs/architecture-light.svg`, or `docs/architecture-dark.svg` on a dark background, in this folder), and start.

### Before you create anything

Check these with reads. If one fails, stop, say why, and create nothing.
- Agent Management and Integration are available to this organization.
- The organization has an LLM provider for Anthropic, OpenAI, Gemini or Mistral (`list_llm_providers`). If it has several, ask which to use. If it has none, offer to add one with the secure form now, and continue when it exists. Azure OpenAI, Azure AI Foundry and AWS Bedrock providers don't work with this sample.
- The names `products-api`, `products-mcp` and `customer-support-agent` are free in the project. If one is taken, ask the user for a different name and create it with that name.

### Steps

1. **Customer Support Agent, first.** It takes the longest, and a refusal shows before anything else exists. In Agent Management, create a platform-hosted Python agent named `customer-support-agent`: app path `/customer-support-agent/agent`, Python 3.11, default chat interface. Its first build and deploy start on their own. If the create is refused, stop and tell the user why.
2. **Products API, while the agent builds.** In Integration, create an integration named `products-api`: type REST API, path `customer-support-agent/products-api`, WSO2 Integrator runtime. Build it and deploy it.
3. **Products MCP server.** Create an integration named `products-mcp`: type `mcp-server`, path `customer-support-agent/products-mcp`, WSO2 Integrator runtime, no environment variables. Build it after `products-api` is deployed, then connect it to the API before deploying it:
   - Connect its configurable `wso2.products_mcp.productsApiUrl` to the Products API's endpoint with `connect_integration` (target integration `products-api`, target endpoint as `list_integration_connections` lists it). The platform then fills in the API's address inside the project.
   - Only if `connect_integration` isn't available: deploy once, then set the same configurable for Development to the **internal** URL of the API's deployed endpoint with `set_configurables`, and deploy again.
   - Deploy it. Agent Management adds it as an MCP proxy on its own; wait until that proxy is listed. Don't change the MCP server's endpoint visibility. If the proxy doesn't appear, tell the user.
4. **Connect the agent.** When the agent's first deploy is done and the proxy is listed:
   - Attach the MCP proxy with the configuration name `PRODUCTS_MCP`, so Agent Management injects `PRODUCTS_MCP_URL` and `PRODUCTS_MCP_API_KEY`.
   - Attach the LLM provider with the configuration name `LLM_PROVIDER`. Use exactly this name: Agent Management then injects `LLM_PROVIDER_URL`, `LLM_PROVIDER_API_KEY` and `LLM_PROVIDER_PROVIDER`. `LLM_PROVIDER_PROVIDER` is the provider's type (`anthropic`, `openai`, `gemini` or `mistralai`); the agent reads it to choose its client and that provider's default model.
   - If the provider isn't Anthropic, check that the agent's environment now has `LLM_PROVIDER_PROVIDER`. If it doesn't, this Agent Management version doesn't pass the provider's type yet: tell the user, and attach an Anthropic provider instead.
   - Deploy the agent again so that it gets the provider and the MCP server.

### When it is done

When the agent is active, tell the user to open **Try It** in Agent Management and ask, for example, "Is the Trailblazer jacket in stock in size M?".

After the user tries the agent, suggest two next steps: open the trace of that question in Agent Management, and add a guardrail to the LLM provider.

## Code

`products-api` and `products-mcp` are Ballerina 2201.14.1 (`bal build`, `bal run`). `agent` is Python 3.11 (`pip install -r requirements.txt`, `python main.py`). See `README.md` for local runs and every environment variable.
