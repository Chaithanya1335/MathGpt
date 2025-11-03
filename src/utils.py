from qdrant_client import QdrantClient
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_mcp_adapters.client import MultiServerMCPClient  
from crewai.llm import LLM
from dotenv import load_dotenv
import os

load_dotenv()

q_key = os.getenv("Qdrant_Api_Key")

Gemini_Api_Key = os.getenv("Gemini_Api_Key")

def get_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2")->HuggingFaceEmbeddings:
    """
    This function loads and returns the Embedding model
    """

    # Loading the model
    embedding_model = HuggingFaceEmbeddings(model=model_name)

    print (f"Embedding Model Loaded ! Diemension is {len(embedding_model.embed_query("hi hello"))}")

    return embedding_model


def get_qdrant_client()->QdrantClient:
    """
    This Function connects with the qdrant clount and returns the client
    """

    qclient = QdrantClient(
        url="https://7b6932f4-9a57-42d5-b9d6-d3004ff8c497.europe-west3-0.gcp.cloud.qdrant.io:6333",
        api_key=q_key,
        timeout=120
    )

    return qclient

def get_mcp_client()->MultiServerMCPClient:
    """
    This Function connects with the MCP server and returns the client
    """

    mcp_client = MultiServerMCPClient(
        {
            "Maths Retriever Tool": {
                "transport": "stdio",
                "command": "python",
                "args": ["Servers/Retriever_Tool.py"]
            },
            "Web Search Tool": {
                "transport": "stdio",
                "command": "python",
                "args": ["Servers/web_search.py"]
            }

        }
    )

    return mcp_client

def get_llm_model(model_name="gemini-2.5-flash")->LLM:

    """
    This Function loads and returns the LLM model
    """

    llm = LLM(
        model = "gemini/gemini-2.5-flash",
        api_key = Gemini_Api_Key,
    )
    
    print("LLM Model Loaded !")
    
    return llm