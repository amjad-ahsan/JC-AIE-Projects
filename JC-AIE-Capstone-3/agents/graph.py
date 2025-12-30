from langgraph.graph import StateGraph, END

from agents.context_agent import context_agent
from agents.supervisor_agent import supervisor_agent
from agents.rag_agent import rag_agent
from agents.recommendation_agent import recommendation_agent
from agents.response_agent import response_agent
from agents.general_agent import general_agent
from agents.state import AgentState

from dotenv import load_dotenv
load_dotenv()
# langraph setup

graph = StateGraph(AgentState)

# noides to connect

graph.add_node("context", context_agent)
graph.add_node("supervisor", supervisor_agent)

graph.add_node("retrieval", rag_agent)
graph.add_node("recommendation", recommendation_agent)
graph.add_node("response", response_agent)

graph.add_node("general", general_agent)

# workflow

graph.set_entry_point("context")

# Context to understand user intent into supervisor
graph.add_edge("context", "supervisor")

# Supervisor will decide route, eiter anime or general chat
graph.add_conditional_edges(
    "supervisor",
    lambda state: state.get("route", "chat"),   # safe default
    {
        "anime": "retrieval",
        "chat": "general"
    }
)

# Anime route
graph.add_edge("retrieval", "recommendation")
graph.add_edge("recommendation", "response")
graph.add_edge("response", END)

# General Chat route
graph.add_edge("general", END)

# compile

app_graph = graph.compile()






