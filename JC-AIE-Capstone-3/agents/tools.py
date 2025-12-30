from langchain.tools import tool
from qdrant_client import QdrantClient
from openai import OpenAI
import re

# PATHS
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

#DOTENV LOAD
import os
from dotenv import load_dotenv

if env_path.exists():
    load_dotenv(env_path)


# keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "anime_docs"

# APOI CLIENTS

client = OpenAI(api_key=OPENAI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# TOOOLLLSS
#Search Anime Tool
@tool
def search_anime(query: str) -> list:
    """
    Search and Retrieve relevant anime entries from the knowledge base using semantic similarity.
    """


    # convert to embedding
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    # retrieve from Qdrant
    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit= 10, # retrieve top 10, can be increase to reduce similar titles inside results.

    )

    # Extract actual points correctly
    points = response.points if hasattr(response, "points") else response

    documents = []

    for p in points:
        if hasattr(p, "payload"):
            payload = p.payload
        elif isinstance(p, dict):
            payload = p.get("payload")

        # since Qdrant return tuple sometimes, additional fixes.
        elif isinstance(p, (list, tuple)) and len(p) >= 3:
            payload = p[2]
        else:
            continue
        if payload:
            documents.append(payload)

    return documents

# UPDATE FROM VERSION 1.0:
# Fixed issues with Qdrant response parsing due to changes in Qdrant client response structure

# UPDATE FROM VERSION 2.0:
# Remove All Tools except search_anime to focus on core functionality and reduce complexity.
# Function will be moved to agents for clearer sturckture 