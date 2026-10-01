"""A2A Grocery — stock a2a-sdk (Google) client against a country agent. No adapter.
pip install a2a-sdk httpx cryptography

Fetches the card, verifies its ES256 signature against the hub keyring (kid a2ag-2026-10), sends one structured read
as a DataPart {skill, params}, then a transacting skill without a bearer to show the typed refusal (DENY_UNLICENSED_AGENT).
Pick any country agent: the hostname is the country code in lower case before .a2a-grocery.ai (the United Kingdom is `uk`).
"""
import asyncio, base64, hashlib, json, sys, urllib.request
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

AGENT = sys.argv[1] if len(sys.argv) > 1 else "https://uk.a2a-grocery.ai"
KEYRING = "https://a2a-grocery.ai/.well-known/jwks.json"
UA = {"User-Agent": "a2a-grocery-kit-example/1.0"}  # the edge refuses requests with no User-Agent


def verify_card(card: dict) -> str:
    """detached JWS over the canonical card (sorted keys, compact separators, UTF-8); raises if the signature does not verify"""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
    unb = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
    b64u = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")
    jwks = json.load(urllib.request.urlopen(urllib.request.Request(KEYRING, headers=UA), timeout=30))
    sig = card["signatures"][0]
    header = json.loads(unb(sig["protected"]))
    k = next(x for x in jwks["keys"] if x["kid"] == header["kid"])
    pub = ec.EllipticCurvePublicNumbers(int.from_bytes(unb(k["x"]), "big"), int.from_bytes(unb(k["y"]), "big"), ec.SECP256R1()).public_key()
    payload = json.dumps({kk: v for kk, v in card.items() if kk != "signatures"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    raw = unb(sig["signature"])
    pub.verify(encode_dss_signature(int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big")), (sig["protected"] + "." + b64u(payload)).encode("ascii"), ec.ECDSA(hashes.SHA256()))
    return header["kid"]


def artifact_data(response) -> dict:
    """the first DataPart of the first artifact in a Task response"""
    task = json.loads(response.model_dump_json(exclude_none=True))
    for artifact in (task.get("result") or {}).get("artifacts") or []:
        for part in artifact.get("parts") or []:
            if isinstance(part.get("data"), dict):
                return part["data"]
    return {}


async def main():
    async with httpx.AsyncClient(timeout=120) as http:
        card = await A2ACardResolver(http, base_url=AGENT).get_agent_card()
        raw_card = json.load(urllib.request.urlopen(urllib.request.Request(AGENT + "/.well-known/agent-card.json", headers=UA), timeout=30))
        print("card:", card.name, "| signature verifies, kid", verify_card(raw_card), "| skills", len(card.skills))
        client = A2AClient(http, agent_card=card)

        def message(skill, params, mid):
            return {"role": "user", "messageId": mid, "parts": [{"kind": "data", "data": {"skill": skill, "params": params}}]}

        read = artifact_data(await client.send_message(SendMessageRequest(id="1", params=MessageSendParams(message=message("get_market_status", {"ingredient": "retinol", "product_type": "raw milk"}, "m1")))))
        print("read:", read.get("jurisdiction_label"), "rule set", read.get("rule_set_version"), "|", ((read.get("result") or {}).get("status") or {}).get("value") if isinstance((read.get("result") or {}).get("status"), dict) else (read.get("result") or {}).get("detail"))
        refused = artifact_data(await client.send_message(SendMessageRequest(id="2", params=MessageSendParams(message=message("get_price", {"presentation_id": "76177-501-10", "substance": "tirzepatide"}, "m2")))))
        print("transacting skill without a bearer:", refused.get("error"), "-", (refused.get("detail") or "")[:90])


if __name__ == "__main__":
    asyncio.run(main())
