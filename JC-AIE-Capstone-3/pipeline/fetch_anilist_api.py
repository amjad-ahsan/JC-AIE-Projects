import requests #ignore the warning about requests being an external dependency
import json
from time import sleep

ANILIST_URL = "https://graphql.anilist.co" # ANILIST GraphQL API endpoint # safest compared to using MAL API.

# GraphQL query to fetch anime data
# We fetch popular anime sorted by popularity in descending order, this can be adjusted as needed, like sorting by score or trending.
# but popularity gives a good mix of well-known and niche titles.

QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, sort: POPULARITY_DESC) {

      id

      title {
        romaji
        english
      }

      description

      genres
      tags {
        name
      }

      format
      episodes
      duration

      averageScore
      popularity
      favourites

      seasonYear
      status

      relations {
        edges {
          relationType
          node {
            id
          }
        }
      }

      isAdult
    }
  }
}
"""


PER_PAGE = 50 # items per page
TARGET = 1500 # You can change the target number of anime to fetch 
# 1000 pages would be faster, but it wont gain you much more data / options.
# 3000 pages would be slower, but might get you some more obscure titles.

# 2000 is a good middle ground. 1 minute of fetching time. and 20 minutes of loading time to Qdrant.

# Version 2.0 Update: Changed Target to 1500 from 2000 to reduce fetch time due to increase in data size per item causing longer load times to Qdrant.

# Total pages to fetch
TOTAL_PAGES = TARGET // PER_PAGE

fetch_anime = []

for page in range(1, TOTAL_PAGES + 1): # Start from page 1, and loop back until reaching TOTAL_PAGES. Total pages is 40 for 2000 items at 50 per page. 40 iterations.
    #Query variables
    variables = {
        "page": page,
        "perPage": PER_PAGE
    }

    response = requests.post(
        ANILIST_URL,
        json={"query": QUERY, "variables": variables}
    )
    response.raise_for_status()
    # Extract anime data from ANILISTAPI # From anylist gitbook examples, the data is in response.json()["data"]["Page"]["media"]
    batch = response.json()["data"]["Page"]["media"]
    fetch_anime.extend(batch)

    print(f"Fetched page {page} total: {len(fetch_anime)}")
    sleep(0.5)   # Don't wanna get banned, so add small delay to avoid continued hammering to the API.


# Since Data directory exist on different folder, 

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)



with open(DATA_DIR / "anilist_cache.json", "w", encoding="utf-8") as f:
    json.dump(fetch_anime, f, indent=2, ensure_ascii=False)


print("Action Complete. Total anime saved:", len(fetch_anime))

# Code complete. data/anilist_cache.json can be pushed to qdrant vector database. 
# If need more data, replace Target with higher value and rerun but remove existing anilist_cache.json first since it will duplicate data.