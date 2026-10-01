# A2A Grocery — the agentic hub for retail grocery procurement

Powered by SCHEMA algo for grocery agentic commerce

> Agent-to-Agent (A2A) + Model Context Protocol (MCP) hub for retail grocery, speciality foods first. Business to business: makers, brand owners, private label, distributors, importers, retailers and their AI agents. Twenty markets on the SCHEMA algo grocery record; ambient, chilled, frozen and fresh; organic, free-from, plant-based, artisan, origin and premium lanes. Call resolve_jurisdiction, then resolve_actor, then gate_transaction before any availability, price, documents, order or handoff tool; those tools refuse without an allow decision. Every record field carries its source page; every response carries notice; every record carries claim_status (listed · claimed · verified). Artificial intelligence makes mistakes. A2A Grocery is an agentic information source, not a recommendation. No ads, ever. No rank for sale. Trade only.

A2A Grocery is built and run by GreenCore Solutions Corp. (github.com/greencore-solutions). This is the public connect kit, MIT.

## The door

<!-- door:begin -->streamable-HTTP, stateless, server name `a2a-grocery`, door version 1.0.0, 19 tools (read from the door's own tools/list at build)<!-- door:end -->

- Endpoint: `https://mcp.a2a-grocery.ai/mcp` — any client that speaks streamable-HTTP: `{ "url": "https://mcp.a2a-grocery.ai/mcp", "transport": "streamable-http" }`
- A2A 0.3.0 JSON-RPC: `https://a2a-grocery.ai/a2a` (the hub) and `https://<country code>.a2a-grocery.ai/a2a` (one market agent per market, for example `fr.a2a-grocery.ai` for France)
- Agent Card: `https://a2a-grocery.ai/.well-known/agent-card.json` (ES256, kid `a2ag-2026-10`; keyring `/.well-known/jwks.json`)
- Setup: https://a2a-grocery.ai/setup · Docs: https://a2a-grocery.ai/docs · Support: https://a2a-grocery.ai/support
- Official MCP Registry: `io.github.greencore-solutions/a2a-grocery` (server.json in this repo)

## The twenty markets

Europe: France, Germany, Italy, Spain, Poland, UK, Netherlands, Belgium, Switzerland. Americas: United States, Canada, Mexico, Brazil. Asia-Pacific: Japan, South Korea, India, Vietnam, Thailand, Singapore, Australia. Every market is a jurisdiction on the record from day one, on one of fourteen rule sets (the seven European Union markets share one food-law set with national riders).

## The gate

Three calls before any price: `resolve_jurisdiction` → `resolve_actor` → `gate_transaction`. Twelve reason codes: ALLOW · REQUIRE_NOTIFICATION · REQUIRE_RESPONSIBLE_PERSON · DENY_NOT_PERMITTED_HERE · DENY_INGREDIENT_BANNED · DENY_INGREDIENT_LIMIT · DENY_CLAIM · DENY_MARKET · DENY_ACTOR_CLASS · DENY_UNLICENSED_AGENT · DENY_NO_GTIN · DENY_NOT_VERIFIED.

## The tools

- **Gate** — `resolve_jurisdiction`, `resolve_actor`, `gate_transaction`
- **SKUs** — `search_cleared_items`, `get_item`, `verify_gtin`, `get_label_and_claims`, `compare_items`
- **Chains** — `find_verified_buyer`, `find_verified_supplier`
- **HITL** (the auditor and documents lane) — `get_product_documents`, `log_audit`
- **Economics** — `get_price`, `get_availability`, `create_order_intent`, `a2a_handoff`
- **Acts** — `get_market_status`, `get_notification_requirements`, `get_enforcement_watch`

Reads are open. The transacting tools take a client-credentials Bearer from the issuer, https://a2a-registry.ai (register at `/oauth/register`; scope `grocery.transact`; see https://a2a-grocery.ai/auth.md).

## Two worked prompts

Buy side — "Find cleared organic dry pasta suppliers for a discounter in Germany, with certificates and availability."

Sell side — "Which retail buyer desks in France take artisan chilled products, and what does each market require on the label?"

## Examples

Stock clients, no adapter: `examples/aws_strands.py` · `examples/azure_semantic_kernel.py` · `examples/google_genai.py` · `examples/generic_mcp_client.py`; A2A: `examples/a2a_aws_strands.py` · `examples/a2a_azure_agent_framework.py` · `examples/a2a_google_sdk.py`.

## Search words

grocery · retail grocery · procurement · supplier · buyer · private label · GTIN · discounter · supermarket · speciality foods · organic · cleared · orderable · AI agent · agent-to-agent · 20 markets · SCHEMA algo · A2A Grocery · agentic hub · Estate AI Agent · GSC Agentic Core

## Pay on it

x402 on https://a2a-x402.ai (USDC on Base, settlement after the gate; a refused order intent is not settled and not charged). Front door: https://a2a-pay.ai.

## Contact

mcp@a2a-grocery.ai — the registry contact for every listing this hub files. A person reads the form at https://a2a-grocery.ai/support.

Built and run by GreenCore Solutions Corp. Artificial intelligence makes mistakes. A2A Grocery is an agentic information source, not a recommendation. No ads, ever. No rank for sale. Trade only.
