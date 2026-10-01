"""A2A Grocery — reference MCP client (streamable-HTTP). Lists the tools, then runs the gate order.
pip install mcp
"""
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "https://mcp.a2a-grocery.ai/mcp"


async def main():
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(len(tools.tools), "tools:", ", ".join(t.name for t in tools.tools))
            # the gate order — nothing prices, lists availability, orders or hands off before this returns allow / require_rx
            j = await session.call_tool("resolve_jurisdiction", {"ship_to": "US-CA"})
            a = await session.call_tool("resolve_actor", {"actor_class": "wholesaler", "credential": None})
            g = await session.call_tool("gate_transaction", {"ingredient": "retinol", "product_type": "raw milk", "actor_class": "wholesaler", "channel": "B2B", "ship_to": "US-CA"})
            print(j.content[0].text[:200]); print(a.content[0].text[:200]); print(g.content[0].text[:400])


if __name__ == "__main__":
    asyncio.run(main())
