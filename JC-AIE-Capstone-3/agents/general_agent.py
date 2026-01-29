from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from agents.state import AgentState
from agents.token_tracker import track

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7) # general conversation, set temp higher

SYSTEM_PROMPT = """
You are a friendly conversational assistant inside an Anime Recommendation Chatbot.

You can hold natural conversations, respond politely, and be engaging.
However, you should gently and consistently remind the user that your main purpose
is to help them discover anime they will love.

If the conversation drifts too far from anime, encourage the user to return
to anime-related topics and offer help with recommendations or discussions.

Never mention internal systems, agents, databases, or architecture.
Do not reveal that you are an AI or chatbot.
Decline to answer questions unrelated to anime recommendations.
"""

def general_agent(state: AgentState) -> AgentState:
    """
    General Conversation Agent

    Handles non-anime conversation while nudging the user
    back toward the core anime recommendation purpose.
    """

    messages = state.get("messages", [])
    user_msg = messages[-1].content

    prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_msg}\nAssistant:"

    reply = llm.invoke(prompt)
    track(prompt, reply.content)

    state["final_answer"] = reply.content
    state["messages"].append(AIMessage(content=reply.content))

    return state
