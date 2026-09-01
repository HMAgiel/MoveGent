import sys
import os
import uuid
from pathlib import Path
import streamlit as st
from chatbot.chatbot_result import run_chatbot

st.set_page_config(
    page_title="MovGent — Movie Agent",
    page_icon="🎬",
    layout="centered",
)


def load_css() -> None:
    """Muat style.css sekali lalu suntikkan ke halaman."""
    css = (Path(__file__).parent / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_header() -> None:
    """Header filmstrip: sprocket atas + wordmark + eyebrow marquee."""
    st.markdown(
        """
        <div class="marquee">
          <div class="marquee-sprockets"></div>
          <div class="marquee-inner">
            <span class="marquee-wordmark">MOVGENT</span>
            <span class="marquee-eyebrow">Now Showing &middot; Movie Agent</span>
          </div>
          <div class="marquee-sprockets"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scene_tag(frame_no: int) -> None:
    """Label frame untuk kartu scene asisten."""
    st.markdown(
        f'<div class="scene-tag">&#127916; Frame {frame_no:03d}</div>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Sidebar: kartu kredit (run terakhir) + chip sesi + tombol reset."""
    with st.sidebar:
        last_run = next(
            (m for m in reversed(st.session_state.messages)
             if m["role"] == "assistant" and "routing" in m),
            None,
        )

        if last_run:
            cost = last_run["cost"]
            inner = f"""
            <div class="credits-row">
              <span class="credits-label">Cast</span>
              <span class="credits-value">{last_run['routing']}</span>
            </div>
            <div class="credits-row">
              <span class="credits-label">Footage</span>
              <span class="credits-value">{last_run['in_tokens']:,} in &middot; {last_run['out_tokens']:,} out</span>
            </div>
            <div class="credits-row">
              <span class="credits-label">Budget</span>
              <span class="credits-value">${cost:.6f}</span>
            </div>
            """
        else:
            inner = '<div class="credits-empty">No run yet — ask a question below.</div>'

        st.markdown(
            f"""
            <div class="credits-card">
              <div class="credits-title">Carte Credits</div>
              <div class="credits-rule"></div>
              {inner}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="session-chip">Session <span class="session-id">{st.session_state.session_id[:8]}</span></div>',
            unsafe_allow_html=True,
        )

        if st.button("Reset conversation", use_container_width=True, key="reset_conversation"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()


load_css()
render_header()
render_sidebar()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat chat
frame_count = 0
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        frame_count += 1
        with st.chat_message("assistant", avatar="🎬"):
            render_scene_tag(frame_count)
            st.markdown(msg["content"])

# Input dari user
if prompt := st.chat_input("Ask anything about movies…"):

    # 1. Simpan pesan user ke history Streamlit DULU
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Panggil chatbot dan tampilkan hasilnya
    with st.chat_message("assistant", avatar="🎬"):
        with st.spinner("Projecting…"):
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

        render_scene_tag(frame_count + 1)
        st.markdown(response_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "routing": routing,
        "in_tokens": in_tokens,
        "out_tokens": out_tokens,
        "total_tokens": total_tokens,
        "cost": cost_in_dollars
    })
