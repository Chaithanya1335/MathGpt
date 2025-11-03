from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.knowledgebase.VectorDB import VectorDB
import sys

# Lazy initialization of retriever
_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = VectorDB().get_retriever()
    return _retriever


# Define the input schema for the tool
class QueryInput(BaseModel):
    """Schema for querying the knowledge base."""
    query: str = Field(..., description="The text query to search for relevant documents.")


# Define the CrewAI tool
class GetRelevantDocumentsTool(BaseTool):
    name: str = "Get Relevant Documents"
    description: str = (
        "Retrieves the most relevant documents from the VectorDB knowledge base "
        "based on a given natural language query."
    )
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, query: str) -> str:
        """Executes the tool logic."""
        if not query:
            return "Error: Empty query provided."

        print(f"Fetching relevant docs for: {query}", file=sys.stderr, flush=True)

        retriever = get_retriever()
        docs = retriever.get_relevant_documents(query)

        if not docs:
            return "No relevant documents found in the knowledge base."

        # Return top 5 results
        results = [d.page_content for d in docs[:5]]
        return "\n\n".join(results)
