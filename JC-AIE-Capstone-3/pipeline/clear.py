import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "anime_docs" # USE THE EXACT SAME NAME AS USED IN load_to_qdrant.py

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

if qdrant.collection_exists(COLLECTION_NAME):
    qdrant.delete_collection(COLLECTION_NAME)
    print("Qdrant collection deleted:", COLLECTION_NAME)
else:
    print("Collection does not exist.")
