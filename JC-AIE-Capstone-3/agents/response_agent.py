from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

from agents.state import AgentState
from agents.token_tracker import track  

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

MAX_HISTORY = 10 # max messages to keep in context

# ensure title consistency
def safe_title(anime):
    title = anime.get("title")

    if isinstance(title, dict):
        return title.get("romaji") or title.get("english") or "Unknown Title"
    elif isinstance(title, str):
        return title
    else:
        return "Unknown Title"

#  convert ranked list to readable text
def format_ranked(ranked):
    if not ranked:
        return "No recommendations available."

    lines = []
    for i, rec in enumerate(ranked, 1):
        anime = rec["anime"]
        title = safe_title(anime)
        reason = rec["reason"]
        score = rec["similarity_score"]

        lines.append(f"{i}. {title} (match: {score:.2f})\n   {reason}")

    return "\n".join(lines)

# agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert anime recommendation assistant.\n\n"

     "Your job is to present high-quality anime recommendations based strictly "
     "on the ranked results provided.\n\n"

     "Response style rules:\n"
     "- Be concise, confident, and professional.\n"
     "- Do NOT repeat the user's question.\n"
     "- Do NOT ask unnecessary follow-up questions.\n"
     "- Avoid generic chatbot phrases (e.g., 'happy watching', 'let me know if').\n"
     "- Keep explanations short and meaningful.\n"
     "- Use structured lists with brief reasons.\n"
     "- Respect user constraints strictly (e.g., 'only TV series').\n"
     "- End with one clear best-match recommendation.\n\n"

     "Never mention internal systems, tools, or the database."
    ),
    MessagesPlaceholder(variable_name="messages"),
    ("human",
     "Here are ranked anime recommendations:\n\n{ranked}\n\n"
     "Respond to the user in a helpful conversational way."
    )
])

# RESPONSE AGENT
def response_agent(state: AgentState) -> AgentState:
    #read state or chat history
    messages = state.get("messages", [])
    ranked = state.get("ranked", [])

    # Memory control, prevents context overload set to 10
    if len(messages) > MAX_HISTORY:
        state["messages"] = messages[-MAX_HISTORY:]
        messages = state["messages"]

    # Off topic or idle handling
    if state.get("user_intent") in ("OFF_TOPIC", "IDLE"):
        user_msg = messages[-1].content
        reply = llm.invoke(user_msg)
        track(user_msg, reply.content)

        state["final_answer"] = reply.content
        state["messages"].append(AIMessage(content=reply.content))
        return state

# IF NOT IN DATABASE OR NO RANK RESULT
    if not ranked:
        answer = (
            "I dont have the perfect match yet — but I can get you there.\n\n"
            "What kind of vibe are you looking for? "
            "You can also name a favorite anime and I will use it as a reference."
        ) # Set answer according to preferences

        state["final_answer"] = answer
        state["messages"].append(AIMessage(content=answer))
        return state

# format ranke results
    ranked_text = format_ranked(ranked)

    formatted = prompt.invoke({
        "messages": messages,
        "ranked": ranked_text
    })

    reply = llm.invoke(formatted)
    track(str(formatted), reply.content)
#Write results back to state/ history
    state["final_answer"] = reply.content
    state["messages"].append(AIMessage(content=reply.content))

    return state



