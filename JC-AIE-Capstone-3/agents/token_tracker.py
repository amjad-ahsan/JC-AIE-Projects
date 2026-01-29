import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o-mini")

def count_tokens(text: str) -> int:
    return len(encoder.encode(text))

def track(prompt: str, response: str):
    import streamlit as st

    tokens = count_tokens(prompt) + count_tokens(response)

    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0

    st.session_state.total_tokens += tokens

