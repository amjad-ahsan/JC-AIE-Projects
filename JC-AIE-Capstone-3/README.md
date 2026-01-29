

# Anime Recommendation Chatbot

Capstone Project — AI Engineering

Live Application:
[https://jc-aie-projects-oresbhnpnk6m2wppvj72hs.streamlit.app/](https://jc-aie-projects-oresbhnpnk6m2wppvj72hs.streamlit.app/)

---

## Project Overview

This project implements an intelligent anime recommendation chatbot using a multi-agent architecture coordinated through LangGraph. The system combines natural language understanding, retrieval-augmented generation (RAG), structured ranking, and conversational response generation into a modular and extensible pipeline.

The primary goal of the project is to provide high-quality, personalized anime recommendations based on user preferences, emotional tone, and semantic intent while maintaining strict enforcement of user-defined constraints such as release year, format, and content restrictions.

---

## System Architecture

The system is built around a shared state model (`AgentState`) and an explicit execution graph defined in `graph.py`. Each user request is processed as a traversal through this graph.

### High-Level Flow

1. **Context Agent**
   Extracts user intent and preferences, including genre, mood, constraints, and semantic description.

2. **Supervisor Agent**
   Routes the request either to the anime recommendation pipeline or to a general conversation pipeline.

3. **Anime Recommendation Pipeline**

   * **RAG Agent**: Performs retrieval from the anime knowledge base, applies hard constraints, and produces candidate results.
   * **Recommendation Agent**: Uses an LLM to rank candidates and applies deterministic validation to guarantee stable output.
   * **Response Agent**: Generates natural language explanations and conversational responses.

4. **General Agent**
   Handles non-anime or idle conversation in a controlled manner.

5. **State Update**
   All agents update a shared state which is returned to the UI and persisted across the session.

---

## Graph Orchestration (LangGraph)

The orchestration layer is implemented using LangGraph. It defines the execution order, routing decisions, and termination points of the system.

Logical structure of the graph:

Context → Supervisor →
• Anime Route: RAG → Recommendation → Response → End
• Chat Route: General → End

This design ensures modularity, maintainability, and clear separation of responsibilities.

---

## Retrieval and Constraint Enforcement

The system distinguishes between **hard constraints** and **soft preferences**:

### Hard Constraints (strictly enforced)

* Release year
* Format (TV, Movie, etc.)
* Status (Finished, Airing)
* Episode count
* Duration
* Adult content flag

If no anime satisfy hard constraints, the system does not violate them and instead requests clarification.

### Soft Preferences (ranking guidance)

* Genres
* Mood
* Description
* Tags
* Reference anime

These guide semantic retrieval and ranking but do not discard candidates on their own.

---

## Recommendation Ranking

The ranking process is handled by an LLM that evaluates candidate anime using:

* User preferences
* Emotional fit
* Genre alignment
* Popularity and quality
* Semantic relevance

A deterministic validation layer enforces:

* Stable number of recommendations
* Unique anime entries
* Bounded similarity scores
* Fallback filling if the LLM returns insufficient results

This guarantees reliable output even under imperfect model behavior.

---

## Response Generation

The response agent converts ranked recommendations into a natural, conversational explanation. It maintains context, avoids internal system references, and provides a final personal recommendation.

---

## User Interface

The application is built with Streamlit and provides:

* Conversational chat interface
* Persistent session memory
* Dynamic source inspection
* System status panel
* Session controls and reset functionality

Live deployment:
[https://jc-aie-projects-oresbhnpnk6m2wppvj72hs.streamlit.app/](https://jc-aie-projects-oresbhnpnk6m2wppvj72hs.streamlit.app/)

---

## Monitoring and Observability

The project integrates Langfuse for tracing and performance monitoring. All LLM calls, graph execution, and major events are logged for debugging, optimization, and evaluation.

---

## Design Principles

* Modular multi-agent architecture
* Deterministic control over probabilistic components
* Clear separation between reasoning, retrieval, ranking, and response
* Strong enforcement of user constraints
* Extensible pipeline for future domains

---

## Summary

This project demonstrates production-style AI system design by combining structured orchestration, retrieval-augmented generation, and controlled language model behavior into a coherent recommendation platform. It prioritizes reliability, maintainability, and user trust while maintaining conversational quality and flexibility.

