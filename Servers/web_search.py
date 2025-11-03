from langchain_community.tools.tavily_search import TavilySearchResults
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from dotenv import load_dotenv
import os, sys, json

load_dotenv()
TAVILY_API_KEY = os.getenv("Tavily_Api_Key")

mcp = FastMCP("Web Search Tool")

class SearchInput(BaseModel):
    query: str

@mcp.tool(
    name="Web_Search_Tool",
    description="Performs a web search to retrieve the most relevant information for a given query."
)
async def web_search_tool(query: str):
    """Perform a web search and return top 5 clean results."""
    print(f"🔍 Performing web search for: {query}", file=sys.stderr, flush=True)

    try:
        search_tool = TavilySearchResults(api_key=TAVILY_API_KEY)

        # Try async run
        if hasattr(search_tool, "arun"):
            result = await search_tool.arun(query)
        else:
            result = search_tool.run(query)

        # Normalize
        if not result:
            return {"message": "No relevant information found."}

        # Tavily sometimes returns a string or list — normalize
        if isinstance(result, str):
            parsed = [line.strip() for line in result.split("\n") if line.strip()]
        elif isinstance(result, list):
            parsed = result
        else:
            parsed = [str(result)]

        # Return a clean JSON dictionary
        return {"query": query, "top_results": parsed[:5]}

    except Exception as e:
        err_msg = f"Tavily search failed: {type(e).__name__} - {str(e)}"
        print(err_msg, file=sys.stderr, flush=True)
        return {"error": err_msg}

if __name__ == "__main__":
    mcp.run(transport="stdio")
