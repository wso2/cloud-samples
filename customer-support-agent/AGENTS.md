# Customer Support Agent

A support agent for Summit Outdoor, a fictional outdoor gear store. Users ask about products, stock and store policies, and the agent answers with live product data through MCP tools. All data is read-only mock data.

Three components run in one project:

```
Customer Support Agent (Agent Management) ──▶ gateway (MCP proxy) ──▶ products-mcp (Integration) ──▶ products-api (Integration)
```

## Explanation

Start with this, before any platform call. Tell it to the user in your own words, in five or six short sentences. Don't add claims that are not in this section.

Writing the agent is the small part of an enterprise agent. Most of the work starts when it runs:

- **See what the agent does.** Choreo Cloud traces each model call and tool call of a hosted agent. When an answer is wrong, the trace shows the step that went wrong.
- **Keep it on track.** The agent reaches its LLM through the Agent Management gateway. Guardrails go there, for example to mask personal data or to stop prompt injection, with no change to the agent code. The LLM keys stay in the platform, not in the code.
- **Make sure it can do the job.** Evaluations score the agent's traces, so you see quality drops before your users do.
- **Connect it to your organization.** The agent uses your organization's APIs and MCP servers through the same gateway. You expose them one time, and you control which agents can use them.

This sample is a first step. It uses some of these points:

- The Customer Support Agent runs in Agent Management, so it has traces from the first question.
- It reads live product data through the Products MCP server, which reads the Products API. This is an organization API that the agent gets as an MCP proxy.
- It gets its LLM and its MCP server from the gateway. Its code holds no keys.

It has no guardrails or evaluations yet. Say this lightly, as what the user can add next, not as a gap.

Then show the architecture diagram (`docs/architecture-light.svg`, or `docs/architecture-dark.svg` on a dark background, in this folder), and continue with "Before you create anything".

## Deploy on Choreo Cloud

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

After the user tries the agent, suggest two next steps: open the trace of that question in Agent Management, and add a guardrail to the LLM provider.

## Code

`products-api` and `products-mcp` are Ballerina 2201.14.1 (`bal build`, `bal run`). `agent` is Python 3.11 (`pip install -r requirements.txt`, `python main.py`). See `README.md` for local runs and every environment variable.
