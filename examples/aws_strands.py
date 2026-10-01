"""A2A Grocery — Strands Agents (AWS) stock MCP client, no adapter.
pip install strands-agents mcp
"""
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

URL = "https://mcp.a2a-grocery.ai/mcp"

client = MCPClient(lambda: streamablehttp_client(URL))
with client:
    tools = client.list_tools_sync()
    print(len(tools), "tools")
    # hand the tools to a Strands Agent as-is:
    # from strands import Agent
    # agent = Agent(tools=tools)
    # agent("Resolve the jurisdiction for a US-CA ship-to, resolve a wholesaler actor, then gate retinol on the licensed-medicine pathway.")
