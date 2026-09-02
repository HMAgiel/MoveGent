import uuid
import streamlit as st
from chatbot.chatbot_result import run_chatbot

st.set_page_config(
    page_title="Chatbot Film",
    page_icon="🤖",
    layout="centered",
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Chatbot Film")
st.caption(f"Session ID: `{st.session_state.session_id}`")

# Tampilkan riwayat chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant" and "routing" in msg:
            with st.expander("📊 Detail Eksekusi & Biaya"):
                st.write(f"**Routing Agen:** `{msg['routing']}`")
                st.write(f"**Tokens:** {msg['in_tokens']} in | {msg['out_tokens']} out | {msg['total_tokens']} total")
                st.write(f"**Estimasi Biaya:** `${msg['cost']:.6f}`")

# Input dari user
if prompt := st.chat_input("Ketik pertanyaan kamu…"):

    # 1. Simpan pesan user ke history Streamlit DULU
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Panggil chatbot dan tampilkan hasilnya
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses…"):
            # 2. Kirim SELURUH list messages ke backend, bukan cuma prompt
            bot_data = run_chatbot(st.session_state.messages) 
            
        response_text = bot_data["response"]
        routing = bot_data["routing"]
        in_tokens = bot_data["input_tokens"]
        out_tokens = bot_data["output_tokens"]
        total_tokens = in_tokens + out_tokens
        
        PRICE_PER_1M_INPUT = 0.15   
        PRICE_PER_1M_OUTPUT = 0.60 
        cost_in_dollars = (in_tokens / 1_000_000 * PRICE_PER_1M_INPUT) + (out_tokens / 1_000_000 * PRICE_PER_1M_OUTPUT)

        st.markdown(response_text)
        
        with st.expander("📊 Detail Eksekusi & Biaya"):
            st.write(f"**Routing Agen:** `{routing}`")
            st.write(f"**Tokens:** {in_tokens} in | {out_tokens} out | {total_tokens} total")
            st.write(f"**Estimasi Biaya:** `${cost_in_dollars:.6f}`")

    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "routing": routing,
        "in_tokens": in_tokens,
        "out_tokens": out_tokens,
        "total_tokens": total_tokens,
        "cost": cost_in_dollars
    })