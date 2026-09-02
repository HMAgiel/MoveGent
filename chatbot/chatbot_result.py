import streamlit as st
import tiktoken
from functools import lru_cache
from langfuse import get_client, propagate_attributes
from langchain_core.messages import HumanMessage, AIMessage
from langfuse.langchain import CallbackHandler
from chatbot.graph.graph import app


@lru_cache(maxsize=1)
def _get_langfuse():
    return get_client()


def _split_history(chat_history: list) -> tuple:
    """Pisahkan query terbaru, riwayat pesan, dan teks gabungan untuk token counting."""
    latest_query = chat_history[-1]["content"]
    past_history = []
    for msg in chat_history[:-1]:
        if msg["role"] == "user":
            past_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            past_history.append(AIMessage(content=msg["content"]))
    input_text_for_counting = " ".join(m["content"] for m in chat_history)
    return latest_query, past_history, input_text_for_counting


def _build_initial_state(latest_query: str, past_history: list) -> dict:
    """State awal untuk invoke graph."""
    return {
        "messages": [HumanMessage(content=latest_query)],
        "history": past_history,
        "SQL_result": "",
        "SQL_missing": "",
        "RAG_result": "",
        "OMDB_result": "",
        "final_result": "",
        "data_worker": "",
        "next_worker": "",
    }


def _count_tokens(text: str) -> int:
    """Hitung token dengan tiktoken; fallback kata*2 bila gagal."""
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return len(text.split()) * 2


def _extract_routing(result: dict) -> str:
    """Buat string routing "a -> b" atau "Direct"."""
    routing_path = []
    if result.get("next_worker"):
        routing_path.append(result["next_worker"])
    if result.get("data_worker"):
        routing_path.append(result["data_worker"])
    return " -> ".join(routing_path) if routing_path else "Direct"


def run_chatbot(chat_history: list) -> dict:
    session_id = st.session_state.session_id
    langfuse = _get_langfuse()

    # 1. Pisahkan pertanyaan terbaru dengan riwayat masa lalu
    latest_query, past_history, input_text_for_counting = _split_history(chat_history)

    with langfuse.start_as_current_observation(
        name="langgraph-supervisor",
        as_type="trace",
        input={"query": latest_query}
    ) as obs:
        with propagate_attributes(session_id=session_id):
            handler = CallbackHandler()

            result = app.invoke(
                _build_initial_state(latest_query, past_history),
                config={
                    "callbacks": [handler],
                    "configurable": {
                        "session_id": session_id,
                        "thread_id": session_id,
                    },
                },
            )

            # Ekstrak Hasil Akhir
            final = result.get("final_result", "_(tidak ada respons)_")
            obs.update(output={"response": final})

            # Ekstrak Routing
            routing_str = _extract_routing(result)

            # Hitung Token Manual
            input_tokens = _count_tokens(input_text_for_counting)
            output_tokens = _count_tokens(final)

            return {
                "response": final,
                "routing": routing_str,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
