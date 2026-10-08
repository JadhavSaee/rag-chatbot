import streamlit as st
from rag import answer

st.set_page_config(page_title="Sunrise Health Clinic Assistant")
st.title("Sunrise Health Clinic Assistant")
st.caption("Ask about timings, doctors, fees and policies.")

if "msgs" not in st.session_state:
    st.session_state.msgs = []

for m in st.session_state.msgs:
    st.chat_message(m["role"]).write(m["content"])

if q := st.chat_input("Ask a question"):
    st.chat_message("user").write(q)
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.msgs]
    try:
        with st.spinner("Thinking..."):
            reply, sources = answer(q, history)
    except Exception:
        reply, sources = "Something went wrong. Please try again.", []
    shown = reply + (f"\n\n*Sources: {', '.join(sources)}*" if sources else "")
    st.chat_message("assistant").write(shown)
    st.session_state.msgs += [
        {"role": "user", "content": q},
        {"role": "assistant", "content": reply},
    ]