"""stamp_readme.py — writes the agents table and the door line into README.md from the wire at the time of the push.
Reads the hub's list_agents over A2A (counts, roles, regions) and the door's health (version, tool count); nothing is typed by hand.
Run before every push: python tools/stamp_readme.py"""
import json, re, pathlib, urllib.request, datetime

README = pathlib.Path(__file__).resolve().parent.parent / "README.md"
UA = {"User-Agent": "a2a-grocery-kit-stamp", "Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
ROLE_LABEL = {
    "hub": "Hub (concierge)", "registry": "Registry (token questions)", "x402": "Payments door (receipt questions)", "country": "Country agents", "actor-entry": "Actor-class entry points",
    "pharma-gate": "Pharma gate", "handoff": "Handoff (referral only)", "watch": "Enforcement watch", "audit": "Auditor Port", "tenant-concierge": "Tenant concierge", "tenant-state": "State and territory agents", "tenant-desk": "Jurisdiction desks",
}
HOST_HINT = {
    "hub": "a2a-grocery.ai", "registry": "a2a-registry.ai", "x402": "a2a-x402.ai", "country": "country code + .a2a-grocery.ai (the United Kingdom is uk; the European Union level is eu)",
    "actor-entry": "pharmacy · prescriber · wholesaler · brand + .a2a-grocery.ai", "pharma-gate": "a2a-pharma.ai", "handoff": "handoff.a2a-grocery.ai", "watch": "watch.a2a-grocery.ai", "audit": "audit.a2a-grocery.ai",
    "tenant-concierge": "grocery-usa.ai", "tenant-state": "us- + state or territory code + .grocery-usa.ai", "tenant-desk": "us · ca · mx · eu · uk · kr · jp · sg · ch + .grocery-usa.ai",
}


def a2a(host, skill, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "message/send", "params": {"message": {"role": "user", "messageId": "stamp", "parts": [{"kind": "data", "data": {"skill": skill, "params": params}}]}}}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(f"https://{host}/a2a", data=body, headers=UA, method="POST"), timeout=120))
    return r["result"]["artifacts"][0]["parts"][0]["data"]


def door():
    h = json.load(urllib.request.urlopen(urllib.request.Request("https://mcp.a2a-grocery.ai/health.json", headers=UA), timeout=30))
    body = b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
    txt = urllib.request.urlopen(urllib.request.Request("https://mcp.a2a-grocery.ai/mcp", data=body, headers=UA, method="POST"), timeout=60).read().decode("utf-8")
    d = next((json.loads(l[5:]) for l in txt.splitlines() if l.startswith("data:")), None) or json.loads(txt)
    return h["version"], len(d["result"]["tools"])


def main():
    la = a2a("a2a-grocery.ai", "list_agents", {"tenant": "all"})
    version, tools = door()
    asof = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    rows = []
    for role in ROLE_LABEL:
        agents = [a for a in la["agents"] if a["role"] == role]
        if not agents:
            continue
        regions = sorted({a["region"] for a in agents})
        rows.append(f"| {ROLE_LABEL[role]} | {HOST_HINT[role]} | {len(agents)} | {' · '.join(regions)} |")
    table = "\n".join(["| Role | Hostname | Agents | Region |", "|---|---|---|---|"] + rows)
    block = (f"<!-- agents:begin -->\n{table}\n\n{la['count']} agents live, {la['reserved']} product-line slots reserved on the tenant table; "
             f"by region: " + " · ".join(f"{k} {v}" for k, v in la["by_region"].items()) + f". Counted from the hub's `list_agents` on {asof}; door version {version}, {tools} tools.\n<!-- agents:end -->")
    s = README.read_text(encoding="utf-8")
    s = re.sub(r"<!-- agents:begin -->.*?<!-- agents:end -->", lambda m: block, s, flags=re.S)
    s = re.sub(r"<!-- door:begin -->.*?<!-- door:end -->", f"<!-- door:begin -->streamable-HTTP, stateless, server name `a2a-grocery`, door version {version}, {tools} tools (read from the wire {asof})<!-- door:end -->", s, flags=re.S)
    README.write_text(s, encoding="utf-8", newline="\n")
    print(json.dumps({"as_of": asof, "agents": la["count"], "reserved": la["reserved"], "by_region": la["by_region"], "by_role": la["by_role"], "door": version, "tools": tools}))


if __name__ == "__main__":
    main()
