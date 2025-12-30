from dotenv import load_dotenv
load_dotenv()

from agents.state import AgentState
from dotenv import load_dotenv
load_dotenv()



def supervisor_agent(state: AgentState) -> AgentState:
    """
    Supervisor Agent

    Writes routing decision into the shared state. 
    Differentiates between anime-related and general chat.
    """

    intent = state.get("user_intent", "GENERAL")

    if intent == "ANIME":
        state["route"] = "anime"
    else:
        state["route"] = "chat"

    return state

