"""A2A Grocery — Microsoft Agent Framework (Azure) stock A2A agent client against a country agent. No adapter.
pip install agent-framework-a2a a2a-sdk httpx cryptography

Resolves the card, verifies its ES256 signature against the hub keyring (kid a2ag-2026-10), sends one structured read,
then a transacting skill without a bearer to show the typed refusal (DENY_UNLICENSED_AGENT).
A2AAgent sends text parts; the endpoint reads a JSON text part as a {skill, params} request (a JSON parse, no inference).
"""
import asyncio, json, sys, urllib.request
import httpx
from a2a.client import A2ACardResolver
from agent_framework_a2a import A2AAgent
from a2a_google_sdk import verify_card  # the same signature check; keep the two files side by side

AGENT = sys.argv[1] if len(sys.argv) > 1 else "https://uk.a2a-grocery.ai"
UA = {"User-Agent": "a2a-grocery-kit-example/1.0"}  # the edge refuses requests with no User-Agent


def artifact_data(response) -> dict:
    """the agent's DataPart, wherever the framework put it in the response (it may carry it as a JSON string)"""
    tree = json.loads(response.model_dump_json()) if hasattr(response, "model_dump_json") else json.loads(json.dumps(response, default=str))

    def walk(o):
        if isinstance(o, str) and o.lstrip().startswith("{"):
            try:
                x = json.loads(o)
                return x if isinstance(x, dict) and "skill" in x else walk(x)
            except Exception:
                return None
        if isinstance(o, dict):
            if isinstance(o.get("data"), dict) and "skill" in o["data"]:
                return o["data"]
            for v in o.values():
                r = walk(v)
                if r:
                    return r
        if isinstance(o, list):
            for v in o:
                r = walk(v)
                if r:
                    return r
        return None

    return walk(tree) or {}


async def main():
    async with httpx.AsyncClient(timeout=120) as http:
        card = await A2ACardResolver(http, base_url=AGENT).get_agent_card()
        raw_card = json.load(urllib.request.urlopen(urllib.request.Request(AGENT + "/.well-known/agent-card.json", headers=UA), timeout=30))
        print("card:", card.name, "| signature verifies, kid", verify_card(raw_card), "| skills", len(card.skills))
        agent = A2AAgent(name="grocery", agent_card=card, url=AGENT + "/a2a", http_client=http)
        read = artifact_data(await agent.run(json.dumps({"skill": "get_market_status", "params": {"ingredient": "retinol", "product_type": "raw milk"}})))
        print("read:", read.get("jurisdiction_label"), "rule set", read.get("rule_set_version"))
        refused = artifact_data(await agent.run(json.dumps({"skill": "get_price", "params": {"presentation_id": "76177-501-10", "substance": "tirzepatide"}})))
        print("transacting skill without a bearer:", refused.get("error"), "-", (refused.get("detail") or "")[:90])


if __name__ == "__main__":
    asyncio.run(main())
