from dotenv import load_dotenv
load_dotenv()

import json
from langchain_openai import ChatOpenAI
from agents.state import AgentState
from agents.token_tracker import track

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_PROMPT = """
You are an expert anime recommendation planner.

Your job is to convert conversation into a structured retrieval plan
for an anime knowledge base. You need to interpret user intent accurately
and extract relevant fields to build a semantic query.

User Intent:
Classify the user's main intent.

Return exactly one of:

"ANIME" — the user is asking about anime, anime recommendations, anime details, or anime-related discussion.
"GENERAL" — everything else (chitchat, life talk, technical questions, unrelated topics, etc).

Rules:
- If the user message involves anime, entertainment, or something that could reasonably be answered using the anime database, return "ANIME".
- Otherwise return "GENERAL".

Available fields in database:
title, description, genres, tags, seasonYear, averageScore, popularity,
format, episodes, duration, status, isAdult, relations.edges[].relationType

Interpretation rules:

Genres:
If the user mentions any anime genre, store them in "genres".
For example: action, drama, romance, comedy, horror, fantasy, sci-fi,
thriller, mystery, sports, slice of life, psychological, supernatural,
mecha, historical, music, adventure, crime, shounen, seinen, josei, shoujo.

Tags & Tropes:
If the user mentions specific themes, tropes, or concepts that appear in anime,
store them in "tags".

Story, Setting & World:
If the user describes the story, world, or setting in natural language,
capture the key phrases in "description_query".

Tone & Emotion:
If the user expresses emotional tone or vibe, store it in "mood".

Time:
- recent, new, modern -> seasonYear >= 2018
- classic, old -> seasonYear <= 2010
- Years mentioned directly -> seasonYear = year
- Season mentioned (e.g., "summer 2020") -> seasonYear = year

Quality & Reception:
- top, great, masterpiece, highly rated -> averageScore >= 80
- popular, mainstream, well known -> popularity >= 50000
- hidden gem, underrated -> popularity <= 15000

Length & Pacing:
- short -> episodes <= 12
- long -> episodes >= 50
- fast paced -> duration <= 20
- slow paced -> duration >= 25

Release & Format:
- completed, finished -> status = FINISHED
- airing, ongoing -> status = RELEASING
- movie, film -> format = MOVIE

Audience:
- family friendly, not adult, for kids -> isAdult = false

Relations:
If the user asks about sequel, prequel, continuation, next season,
spin-off, side story, adaptation, or related content,
set relation_intent and reference_anime.

Return ONLY valid JSON. Omit unknown fields.

Return format:

{
  "user_intent": "ANIME" | "GENERAL",
  "genres": [],
  "tags": [],
  "year_filter": {"gte": number, "lte": number},
  "episodes_filter": {"gte": number, "lte": number},
  "duration_filter": {"gte": number, "lte": number},
  "min_score": number,
  "min_popularity": number,
  "max_popularity": number,
  "format": string,
  "status": string,
  "isAdult": boolean,
  "reference_anime": string,
  "relation_intent": string,
  "mood": string,
  "description_query": string
}
"""
# Cost effective to run or not function
TRIGGER_WORDS = {
    "recommend", "suggest", "anime", "watch", "find", "similar",
    "looking", "new", "recent", "classic", "top", "best"
}
# Allowing what to update 
ALLOWED_KEYS = {
    "genres", "tags", "year_filter", "episodes_filter",
    "duration_filter", "min_score", "min_popularity",
    "max_popularity", "format", "status", "isAdult",
    "reference_anime", "relation_intent", "mood", "description_query"
}
# Function to run or not, basically a helper function
def run_or_not(text: str) -> bool:
    text = text.lower()
    if len(text.split()) > 5:
        return True
    return any(word in text for word in TRIGGER_WORDS)

def extract_json(text: str) -> dict:
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except:
        return {}


# Context Agent
def context_agent(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content

    if not run_or_not(last_msg):
        state["user_intent"] = "GENERAL"
        state["refined_query"] = last_msg
        return state

    history = "\n".join(m.content for m in state["messages"][-10:]) # Can adjust history length later. 
    prompt = f"{SYSTEM_PROMPT}\n\nConversation:\n{history}"

    response = llm.invoke(prompt)
    track(prompt, response.content)

    intent = extract_json(response.content)

    raw_intent = intent.get("user_intent", "").upper()
    if raw_intent not in {"ANIME", "GENERAL"}:
        raw_intent = "GENERAL"

    state["user_intent"] = raw_intent

    prefs = state.setdefault("user_preferences", {})

    for key, value in intent.items():
        if key in ALLOWED_KEYS and value is not None:
            if isinstance(value, list):
                old = set(prefs.get(key, []))
                prefs[key] = list(old.union(value))
            else:
                prefs[key] = value

    query_parts = []

    if prefs.get("mood"):
        query_parts.append(prefs["mood"])
    if prefs.get("description_query"):
        query_parts.append(prefs["description_query"])
    if prefs.get("reference_anime"):
        query_parts.append(f"similar to {prefs['reference_anime']}")
    if prefs.get("genres"):
        query_parts.extend(prefs["genres"])
    if prefs.get("tags"):
        query_parts.extend(prefs["tags"])

    state["refined_query"] = " ".join(query_parts) if query_parts else last_msg

    return state





