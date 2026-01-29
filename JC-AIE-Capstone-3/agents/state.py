from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

# ANILIST Info fromQDRANT
class AnimeInfo(TypedDict):
    id: int
    title: dict
    genres: List[str]
    description: str
    seasonYear: int
    averageScore: int
    popularity: int

# Rank Recommendation Entry
class Recommendation(TypedDict):
    anime: AnimeInfo
    reason: str
    similarity_score: float

# USer preferences
class UserPreferences(TypedDict, total=False):
    favorite_genres: List[str]
    disliked_genres: List[str]
    preferred_era: str
    watched_titles: List[str]
    mood: str

# Global shared memory
class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]              # memory
    docs: List[AnimeInfo]                    
    ranked: List[Recommendation]             
    last_anime: Optional[AnimeInfo]          # Current topic
    user_preferences: UserPreferences        # Session preferences
    final_answer: Optional[str]              

# Intent routing
    user_intent: str                        # "ANIME" or "GENERAL"
    route: str                              # "anime" or "chat"
    refined_query: str                     # for context 


