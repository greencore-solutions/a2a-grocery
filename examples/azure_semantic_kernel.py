"""A2A Grocery — Semantic Kernel (Azure) stock MCP plugin, no adapter.
pip install semantic-kernel
"""
import asyncio
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin

URL = "https://mcp.a2a-grocery.ai/mcp"


async def main():
    plugin = MCPStreamableHttpPlugin(name="a2a_grocery", url=URL)
    await plugin.connect()
    listed = await plugin.session.list_tools()
    print(len(listed.tools), "tools")
    # kernel.add_plugin(plugin) — the twenty tools become kernel functions under the plugin name
    await plugin.close()


if __name__ == "__main__":
    asyncio.run(main())
