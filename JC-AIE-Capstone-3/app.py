import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agents.graph import app_graph
from langfuse.callback import CallbackHandler
import time
import uuid

load_dotenv()
langfuse_handler = CallbackHandler()

st.set_page_config(page_title="Anime Recommendation Chat", layout="centered")
st.sidebar.header("Control Sidebar")
st.title("Anime Recommendation Helper")

# Intro

with st.expander("About This System", expanded=True):
    st.markdown("""
This application provides personalized anime recommendations based on user preferences, viewing history, and conversational input.

### Usage Guidelines
- Describe the type of anime you are looking for (genres, themes, mood, era, etc.).
- Ask for recommendations similar to titles you enjoy.
- Refine results using constraints such as format, length, or release period.

### Interaction Rules
- Please keep requests related to anime or entertainment content.
- You may refine your preferences at any time during the session.
- The system retains context within the current session.
""")

# State / History

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_docs" not in st.session_state:
    st.session_state.last_docs = []

if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {}

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

# Chat

user_input = st.chat_input("Describe the type of anime you are looking for")

if user_input:
    initial_state = {
        "messages": st.session_state.messages + [HumanMessage(content=user_input)],
        "user_preferences": st.session_state.user_preferences,
        "docs": [],
        "ranked": [],
        "final_answer": None
    }

    start = time.time()

    with st.spinner("Processing request..."):
        result = app_graph.invoke(
            initial_state,
            config={"callbacks": [langfuse_handler]}
        )

    elapsed = time.time() - start

    # Save results
    st.session_state.messages = result["messages"]
    st.session_state.last_docs = result.get("docs", [])
    st.session_state.user_preferences = result.get("user_preferences", {})

    # Sidebar system status
    mode = "Recommendation Mode" if result.get("route") == "anime" else "General Conversation"
    st.sidebar.markdown("System Status")
    st.sidebar.markdown(f"Mode: {mode}")
    st.sidebar.markdown(f"Response time: {elapsed:.2f} seconds")

# Display

for msg in st.session_state.messages:
    role = "User" if msg.type == "human" else "Assistant"
    with st.chat_message(role.lower()):
        st.markdown(msg.content)

# Rag

if st.session_state.last_docs:
    with st.expander("Reference Data"):
        for d in st.session_state.last_docs[:5]:
            title_data = d.get("title")

            if isinstance(title_data, dict):
                title = title_data.get("english") or title_data.get("romaji") or "Unknown Title"
            else:
                title = title_data or "Unknown Title"

            year = d.get("seasonYear", "Unknown")
            st.markdown(f"- {title} ({year})")

# sidebar for UI

if st.sidebar.button("Clear Session"):
    st.session_state.messages = []
    st.session_state.last_docs = []
    st.session_state.user_preferences = {}
    st.session_state.total_tokens = 0
    st.rerun()

st.sidebar.markdown("Usage Metrics")
st.sidebar.markdown(f"Total tokens used: {st.session_state.total_tokens}")




















