"""A2A Grocery — Strands Agents (AWS) stock A2A client provider against a country agent. No adapter.
pip install strands-agents strands-agents-tools cryptography

Discovers the card, verifies its ES256 signature against the hub keyring (kid a2ag-2026-10), sends one structured read,
then a transacting skill without a bearer to show the typed refusal (DENY_UNLICENSED_AGENT).
The provider sends text parts; the endpoint reads a JSON text part as a {skill, params} request (a JSON parse, no inference).
"""
import asyncio, json, sys
from strands_tools.a2a_client import A2AClientToolProvider
from a2a_google_sdk import verify_card  # the same signature check; keep the two files side by side
import urllib.request

AGENT = sys.argv[1] if len(sys.argv) > 1 else "https://uk.a2a-grocery.ai"
UA = {"User-Agent": "a2a-grocery-kit-example/1.0"}  # the edge refuses requests with no User-Agent


def artifact_data(task) -> dict:
    """the agent's DataPart, wherever the provider put it in the task it returns"""
    tree = task if isinstance(task, dict) else json.loads(json.dumps(task, default=str))

    def walk(o):
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
    provider = A2AClientToolProvider(known_agent_urls=[AGENT])
    raw_card = json.load(urllib.request.urlopen(urllib.request.Request(AGENT + "/.well-known/agent-card.json", headers=UA), timeout=30))
    print("card:", raw_card["name"], "| signature verifies, kid", verify_card(raw_card), "| skills", len(raw_card["skills"]))
    # the provider's tools (a2a_discover_agent, a2a_list_discovered_agents, a2a_send_message) are what a Strands Agent would call;
    # here they are called directly so the exchange is visible
    read = artifact_data(await provider._send_message(message_text=json.dumps({"skill": "get_market_status", "params": {"ingredient": "retinol", "product_type": "raw milk"}}), target_agent_url=AGENT))
    print("read:", read.get("jurisdiction_label"), "rule set", read.get("rule_set_version"))
    refused = artifact_data(await provider._send_message(message_text=json.dumps({"skill": "get_price", "params": {"presentation_id": "76177-501-10", "substance": "tirzepatide"}}), target_agent_url=AGENT))
    print("transacting skill without a bearer:", refused.get("error"), "-", (refused.get("detail") or "")[:90])
    # hand the provider to an agent as-is:
    # from strands import Agent
    # agent = Agent(tools=provider.tools)


if __name__ == "__main__":
    asyncio.run(main())
