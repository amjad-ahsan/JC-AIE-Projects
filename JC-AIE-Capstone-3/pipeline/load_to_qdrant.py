
import json

#since we are pushing heavy data, use logging for better visibility.
import logging
from qdrant_client.http.models import VectorParams, Distance, HnswConfigDiff, OptimizersConfigDiff

#For Key 
from openai import OpenAI
from tqdm import tqdm
from qdrant_client import QdrantClient

# .env load
import os
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "anilist_cache.json"

# KEY. From .env
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Name of the Collenction in Vector Database
COLLECTION_NAME = "anime_docs"

# OPENAI API KEY
client = OpenAI(api_key=OPENAI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    # Fixes, for timeout during pushes.
    timeout=120,
)

# load data
with open(DATA_PATH, "r", encoding="utf-8") as f:
    anime_list = json.load(f)

print(f"Loaded {len(anime_list)} anime entries")

# SETI{}
EMBED_DIM = 1536
BATCH_SIZE = 32

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")



# Previous fixes since, previous document existed inside Qdrant.
try:
    qdrant.delete_collection(COLLECTION_NAME)
except:
    pass

qdrant.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    hnsw_config=HnswConfigDiff(on_disk=False),
    optimizers_config=OptimizersConfigDiff(indexing_threshold=0)
)

points = []
total_inserted = 0
id_counter = 0



for anime in tqdm(anime_list):
    description = (anime.get("description") or "").strip()
    if not description:
        continue

    title_obj = anime.get("title") or {}
    title = title_obj.get("english") or title_obj.get("romaji") or title_obj.get("native") or "Unknown Title"

    genres = anime.get("genres") or []
    tags = [t["name"] for t in anime.get("tags", [])]
    format_type = anime.get("format")
    episodes = anime.get("episodes") or "N/A"
    duration = anime.get("duration")
    avg_score = anime.get("averageScore")
    popularity = anime.get("popularity")
    favourites = anime.get("favourites")
    season_year = anime.get("seasonYear")
    status = anime.get("status")
    relations = [
        {"id": r["node"]["id"], "type": r["relationType"]}
        for r in anime.get("relations", {}).get("edges", [])
    ]
    is_adult = anime.get("isAdult", False)


#Format text for embedding
    text = f"""
Title: {title}
Genres: {', '.join(genres)}
Tags: {', '.join(tags)}
Format: {format_type}
Episodes: {episodes}
Duration: {duration}
Average Score: {avg_score}
Popularity: {popularity}
Favourites: {favourites}
Season Year: {season_year}
Status: {status}

Description:
{description}
"""


# Embeddings
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    points.append({
        "id": id_counter,
        "vector": embedding,
        "payload": {
            "id": anime.get("id"),
            "title": title,
            "description": description,
            "genres": genres,
            "tags": tags,
            "format": format_type,
            "episodes": episodes,
            "duration": duration,
            "averageScore": avg_score,
            "popularity": popularity,
            "favourites": favourites,
            "seasonYear": season_year,
            "status": status,
            "relations": relations,
            "isAdult": is_adult,
            "text": text,
        },
    })

    id_counter += 1

    if len(points) >= BATCH_SIZE:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
        total_inserted += len(points)
        points = []

if points:
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    total_inserted += len(points)

print("Completed. Qdrant inserted:", total_inserted)


