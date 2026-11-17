# Customer Support Agent

A support agent for Summit Outdoor, a fictional outdoor gear store. Users ask about products, stock and store policies, and the agent answers with live product data through MCP tools. All data is read-only mock data.

Before deploying, show the user what this sample is: the description and the architecture diagram (`docs/architecture-light.svg`, or `docs/architecture-dark.svg` on a dark background, in this folder) from `README.md`.

Three components run in one project:

```
Customer Support Agent (Agent Management) ──▶ gateway (MCP proxy) ──▶ products-mcp (Integration) ──▶ products-api (Integration)
```

## Deploy on WSO2 Cloud

Deploy all three into the project that the user selected, to the Development environment. Repository: `https://github.com/wso2/cloud-samples`, branch `master`. The sample is in the `customer-support-agent` folder, so every path below starts with it. Use these values as they are. Don't ask the user for the repository, the branch or a folder.

### Before you create anything

Check these with reads. If one fails, stop, say why, and create nothing.
- Agent Management and Integration are available to this organization.
- The organization has an Anthropic LLM provider (`list_llm_providers`). If it has none, offer to add one with the secure form now, and continue when it exists.
- The names `products-api`, `products-mcp` and `customer-support-agent` are free in the project. If one is taken, ask the user for a different name and create it with that name.

Then say the plan in one or two sentences: three parts in this project, ready in about 15 minutes.

### Steps

1. **Customer Support Agent, first.** It takes the longest, and a refusal shows before anything else exists. In Agent Management, create a platform-hosted Python agent named `customer-support-agent`: app path `/customer-support-agent/agent`, Python 3.11, default chat interface. Its first build and deploy start on their own. If the create is refused, stop and tell the user why.
2. **Products API, while the agent builds.** In Integration, create an integration named `products-api`: type REST API, path `customer-support-agent/products-api`, WSO2 Integrator runtime. Build it and deploy it.
3. **Products MCP server.** Create an integration named `products-mcp`: type `mcp-server`, path `customer-support-agent/products-mcp`, WSO2 Integrator runtime, no environment variables. Build it after `products-api` is deployed, then connect it to the API before deploying it:
   - Connect its configurable `wso2.products_mcp.productsApiUrl` to the Products API's endpoint with `connect_integration` (target integration `products-api`, target endpoint as `list_integration_connections` lists it). The platform then fills in the API's address inside the project.
   - Only if `connect_integration` isn't available: deploy once, then set the same configurable for Development to the **internal** URL of the API's deployed endpoint with `set_configurables`, and deploy again.
   - Deploy it. Agent Management adds it as an MCP proxy on its own; wait until that proxy is listed. Don't change the MCP server's endpoint visibility. If the proxy doesn't appear, tell the user.
4. **Connect the agent.** When the agent's first deploy is done and the proxy is listed:
   - Attach the MCP proxy, with the environment variable names `PRODUCTS_MCP_URL` for its URL and `MCP_API_KEY` for its key, so Agent Management injects both.
   - Attach the Anthropic LLM provider, with the environment variable names `LLM_PROVIDER_URL` and `LLM_PROVIDER_KEY`.
   - Deploy the agent again so that it gets the provider and the MCP server.

When the agent is active, tell the user to open **Try It** in Agent Management and ask, for example, "Is the Trailblazer jacket in stock in size M?".

## Code

`products-api` and `products-mcp` are Ballerina 2201.14.1 (`bal build`, `bal run`). `agent` is Python 3.11 (`pip install -r requirements.txt`, `python main.py`). See `README.md` for local runs and every environment variable.
