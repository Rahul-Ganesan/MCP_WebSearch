from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
import os, json

load_dotenv()  # this will read .env into environment variables

# Create an MCP server
mcp = FastMCP(
    name="Test For Search",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)

Tavily_key = os.getenv("TAVILY_API_KEY")


@mcp.tool()
def say_hello(name: str) -> str:
    """Say hello to someone

    Args:
        name: The person's name to greet
    """
    return f"Hello, {name}! Nice to meet you."


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers

    Args:
        a: The first number
        b: The second number
    """
    return a + b


@mcp.tool()
def web_search(query: str) -> str:
    """Perform a web search and return the results.

    Args:
        query: The search query string.

    Returns:
        A string containing the search results.
    """

    tavily_client = TavilyClient(api_key=Tavily_key)
    response = tavily_client.search(query=query, num_results=2)
    merged_content = " ".join(item['content'] for item in response['results'] if item.get('content'))
    return merged_content

# Run the server
if __name__ == "__main__":
    # result = web_search("Who is Harris Jayaraj?")
    # print("Search result:", result)
    mcp.run(transport="streamable-http") 