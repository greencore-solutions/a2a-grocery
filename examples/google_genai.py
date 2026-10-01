"""A2A Grocery — google-genai (stock) with the door's tools as function declarations; the MCP ClientSession dispatches the call.
pip install google-genai mcp
This is google-genai's documented manual pattern (declarations from tools/list, the model chooses, the session executes) because passing the
ClientSession itself as a tool trips the SDK's own deep-copy of the tool list on stock releases; this path runs unpatched. The door needs no adapter.
"""
import asyncio, json, os
from google import genai
from google.genai import types
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "https://mcp.a2a-grocery.ai/mcp"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
PROMPT = "Call gate_transaction with substance retinol, pathway licensed_medicine, actor_class wholesale_distributor, ship_to US-CA."


def strip(schema):
    """the declaration schema: the door's open input schema minus the keys the SDK does not take"""
    if isinstance(schema, dict):
        return {k: strip(v) for k, v in schema.items() if k not in ("additionalProperties", "$schema", "title", "default")}
    if isinstance(schema, list):
        return [strip(x) for x in schema]
    return schema


async def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            declarations = [types.FunctionDeclaration(name=t.name, description=(t.description or "")[:500], parameters=strip(t.inputSchema)) for t in tools]
            config = types.GenerateContentConfig(tools=[types.Tool(function_declarations=declarations)], temperature=0, automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
            first = await client.aio.models.generate_content(model=MODEL, contents=PROMPT, config=config)
            call = next((p.function_call for c in first.candidates for p in c.content.parts if getattr(p, "function_call", None)), None)
            if not call:
                print("the model made no call:", (first.text or "")[:200]); return
            result = await session.call_tool(call.name, dict(call.args))
            answer = result.structuredContent or json.loads(result.content[0].text)
            print(call.name, "->", answer.get("result"), answer.get("reason_code"), "rule set", answer.get("rule_set_version"))
            second = await client.aio.models.generate_content(model=MODEL, config=config, contents=[
                types.Content(role="user", parts=[types.Part(text=PROMPT)]), first.candidates[0].content,
                types.Content(role="user", parts=[types.Part.from_function_response(name=call.name, response={"result": answer})])])
            print((second.text or "").strip()[:300])


if __name__ == "__main__":
    asyncio.run(main())
