from dotenv import load_dotenv
load_dotenv()

import json
from langchain_openai import ChatOpenAI
from agents.state import AgentState
from agents.token_tracker import track

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_PROMPT = """
You are an expert anime recommendation engine.

Your task:
Given the user's preferences and a list of candidate anime results,
select the best matching titles and rank them from best to worst.

Ranking criteria (in priority order):
1. Relevance to the user's request and stated preferences
2. Genre and theme alignment
3. Emotional and tonal fit
4. Overall quality (averageScore)
5. Popularity and cultural impact

Instructions:
- Be objective and precise.
- Do not use flowery language.
- Focus on why each anime is a good match for THIS user.
- Prefer quality and relevance over quantity.
- Select up to 5 results, but fewer if appropriate.

Return ONLY valid JSON in the following format:

[
  {
    "anime_id": number,
    "reason": string,
    "similarity_score": number
  }
]

Rules:
- similarity_score must be between 0.0 and 1.0
- Do not repeat anime_id
- Do not include any text outside the JSON array
- Avoid recommending anime that is not a series(e.g. movies, ova . . . etc) first unless asked.
"""

# recommendation agent

def recommendation_agent(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content.lower()

    # reuse prvious ranking on follow-ups
    if state.get("ranked") and not any(w in last_msg for w in ["new", "different", "another"]):
        return state

    docs = state.get("docs", [])
    prefs = state.get("user_preferences", {})

    if not docs:
        state["ranked"] = []
        return state

    payload = {
        "preferences": prefs,
        "results": docs
    }

    prompt = f"{SYSTEM_PROMPT}\n\n{json.dumps(payload, ensure_ascii=False)}"
    response = llm.invoke(prompt)
    track(prompt, response.content)

    # JSON parse fixes

    try:
        ranked_raw = json.loads(response.content)
    except Exception:
        ranked_raw = []
# IF FAILED FALL BACKS
    if not ranked_raw:
        # Deterministic fallback: high score + popularity
        ranked_raw = [
            {
                "anime_id": d["id"],
                "reason": "Strong overall quality and popularity",
                "similarity_score": 0.6
            }
            for d in sorted(
                docs,
                key=lambda x: (x.get("averageScore", 0), x.get("popularity", 0)),
                reverse=True
            )[:5]
        ]

    ranked = []
    used_ids = set()

    for item in ranked_raw:
        anime_id = item.get("anime_id")
        anime = next((d for d in docs if d["id"] == anime_id), None)

        if not anime or anime_id in used_ids:
            continue

        used_ids.add(anime_id)

        score = item.get("similarity_score", 0.5)
        try:
            score = float(score)
        except:
            score = 0.5

        score = max(0.0, min(score, 1.0))

        ranked.append({
            "anime": anime,
            "reason": item.get("reason", "Good match for your preferences"),
            "similarity_score": score
        })

        if len(ranked) >= 10:
            break

    state["ranked"] = ranked
    return state







