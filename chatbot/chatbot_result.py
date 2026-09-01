import uuid
import streamlit as st
import tiktoken
from langfuse import get_client, propagate_attributes
from langchain_core.messages import HumanMessage, AIMessage
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv
from chatbot.graph.graph import app

load_dotenv()
langfuse = get_client()

langgraph_app = app
def run_chatbot(chat_history: list) -> dict:
    session_id = st.session_state.session_id

    # 1. Pisahkan pertanyaan terbaru dengan riwayat masa lalu
    latest_query = chat_history[-1]["content"] # Pesan paling terakhir
    
    past_history = []
    for msg in chat_history[:-1]: # Ambil SEMUA pesan KECUALI yang terakhir
        if msg["role"] == "user":
            past_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            past_history.append(AIMessage(content=msg["content"]))

    input_text_for_counting = " ".join([m["content"] for m in chat_history])

    with langfuse.start_as_current_observation(
        name="langgraph-supervisor",
        as_type="trace",
        input={"query": latest_query}
    ) as obs:
        with propagate_attributes(session_id=session_id):
            handler = CallbackHandler()

            result = langgraph_app.invoke(
                {
                    "messages": [HumanMessage(content=latest_query)], 
                    "history": past_history,                         
                    "SQL_result": "",
                    "RAG_result": "",
                    "OMDB_result": "",
                    "final_result": "",
                    "data_worker": "",
                    "next_worker": ""
                },
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
            routing_path = []
            if result.get("next_worker"):
                routing_path.append(result["next_worker"])
            if result.get("data_worker"):
                routing_path.append(result["data_worker"])
            routing_str = " -> ".join(routing_path) if routing_path else "Direct"

            # Hitung Token Manual
            try:
                enc = tiktoken.get_encoding("cl100k_base")
                input_tokens = len(enc.encode(input_text_for_counting))
                output_tokens = len(enc.encode(final))
            except Exception:
                input_tokens = len(input_text_for_counting.split()) * 2
                output_tokens = len(final.split()) * 2

            return {
                "response": final,
                "routing": routing_str,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }