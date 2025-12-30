from agents.state import AgentState
from agents.tools import search_anime
from dotenv import load_dotenv

load_dotenv()

# retrieval query builder

def retrieval_query(state: AgentState) -> str:
    prefs = state.get("user_preferences", {})
    parts = []

    if prefs.get("genres"):
        parts.append(" ".join(prefs["genres"]))

    if prefs.get("mood"):
        parts.append(prefs["mood"])

    if prefs.get("description_query"):
        parts.append(prefs["description_query"])

    if prefs.get("reference_anime"):
        parts.append(f"similar to {prefs['reference_anime']}")

    # Fallback
    if not parts:
        return state["messages"][-1].content

    return " | ".join(parts)


# -filter constraints

def filter_contraints(docs, prefs):
    results = []

    for d in docs:
        yf = prefs.get("year_filter")
        if yf:
            y = d.get("seasonYear")
            if y is None:
                continue
            if "gte" in yf and y < yf["gte"]:
                continue
            if "lte" in yf and y > yf["lte"]:
                continue

        ef = prefs.get("episodes_filter")
        if ef:
            ep = d.get("episodes")
            if ep is not None:
                if "gte" in ef and ep < ef["gte"]:
                    continue
                if "lte" in ef and ep > ef["lte"]:
                    continue

        df = prefs.get("duration_filter")
        if df:
            dur = d.get("duration")
            if dur is not None:
                if "gte" in df and dur < df["gte"]:
                    continue
                if "lte" in df and dur > df["lte"]:
                    continue

        if prefs.get("min_score") and (d.get("averageScore") or 0) < prefs["min_score"]:
            continue
        if prefs.get("min_popularity") and (d.get("popularity") or 0) < prefs["min_popularity"]:
            continue
        if prefs.get("max_popularity") and (d.get("popularity") or 0) > prefs["max_popularity"]:
            continue

        if prefs.get("format") and d.get("format") != prefs["format"]:
            continue
        if prefs.get("status") and d.get("status") != prefs["status"]:
            continue

        if prefs.get("isAdult") is not None and d.get("isAdult") != prefs["isAdult"]:
            continue

        results.append(d)

    return results



# rag agent

def rag_agent(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content.lower()

    # reuuse previous docs on follow-ups
    if state.get("docs") and not any(w in last_msg for w in ["new", "recent", "different"]):
        return state

    prefs = state.get("user_preferences", {})

    query = retrieval_query(state)

    raw_docs = search_anime.invoke({"query": query})
    docs = filter_contraints(raw_docs, prefs)

    #  if to few results, fill with raw
    if not docs:
        docs = raw_docs[:10]

    # ranking by score + popularity
    docs = sorted(
        docs,
        key=lambda x: ((x.get("averageScore") or 0), (x.get("popularity") or 0)),
        reverse=True
    )

    # Store most relevant anime
    if docs:
        state["last_anime"] = docs[0]

    # Deduplicate
    seen = set()
    unique_docs = []
    for d in docs:
        if d["id"] not in seen:
            seen.add(d["id"])
            unique_docs.append(d)

    state["docs"] = unique_docs
    return state





