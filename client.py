import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import OpenAI
import os
from dotenv import load_dotenv
import json, ast

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")

client = OpenAI(
     base_url=f"{AZURE_ENDPOINT}",
    api_key=OPENAI_API_KEY
)
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")

async def main():
    async with streamablehttp_client("http://127.0.0.1:8050/mcp") as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("✅ Connected to MCP server!")

            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")


            while True:
                user_input = input("\nAsk me anything (or type 'quit' to exit): ")
                if user_input.lower() == "quit":
                    break

                # Generate search query using Azure OpenAI (new API)
                llm_response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Convert user questions into concise web search queries."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
            )

                query = llm_response.choices[0].message.content.strip()
                print(f"🔎 LLM suggests search query: {query}")

                # Call MCP web_search tool
                response = await session.call_tool("web_search", {"query": query})
                # print("\n--- Search Results ---")
                # print(response)

                # Step 3: Summarize all search results into one concise answer
                summary_response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"""
                I have multiple web search results. Read through all the content below and generate one concise, coherent summary in your own words. Do not just repeat the content. Focus on the key facts.

                {response}
                """}
                    ],
                )

                concise_summary = summary_response.choices[0].message.content.strip()
                print(f"\n💡 Final Summary:\n{concise_summary}")

if __name__ == "__main__":
    asyncio.run(main())
