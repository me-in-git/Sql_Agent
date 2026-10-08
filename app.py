"""Streamlit UI for QueryMind: ask questions about the Chinook database in plain English."""

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from querymind import ReadOnlyDatabase, SQLAgent

load_dotenv()
st.set_page_config(page_title="QueryMind", layout="wide")
st.title("QueryMind")
st.caption("Natural-language questions → read-only SQL over the Chinook music store database")


@st.cache_resource
def get_db() -> ReadOnlyDatabase:
    return ReadOnlyDatabase()


def get_agent() -> SQLAgent | None:
    if "agent" not in st.session_state:
        from querymind.llm import OpenAICompatibleLLM

        try:
            st.session_state.agent = SQLAgent(OpenAICompatibleLLM(), get_db())
        except RuntimeError as exc:
            st.error(f"{exc}. Copy `.env.example` to `.env` and add a key (Groq keys are free).")
            return None
        st.session_state.turns = []
    return st.session_state.agent


with st.sidebar:
    st.header("Database")
    db = get_db()
    for (table,) in db.run("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").rows:
        count = db.run(f'SELECT COUNT(*) FROM "{table}"').rows[0][0]
        st.write(f"`{table}` — {count:,} rows")
    if st.button("Clear conversation"):
        st.session_state.pop("agent", None)
        st.rerun()
    st.markdown("**Try:**\n- Which artist generated the most revenue?\n- And the top 3 genres?\n"
                "- How many tracks have never been purchased?\n- Who does Steve Johnson report to?")

agent = get_agent()
if agent:
    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.write(turn.question)
        with st.chat_message("assistant"):
            st.write(turn.answer)
            if turn.sql:
                st.code(turn.sql, language="sql")
            if turn.result is not None and turn.result.rows:
                st.dataframe(pd.DataFrame(turn.result.rows, columns=turn.result.columns), hide_index=True)
                if turn.result.truncated:
                    st.caption(f"Showing the first {len(turn.result.rows)} rows.")
            failed = [a for a in turn.attempts if a.error]
            if failed:
                with st.expander(f"{len(failed)} failed attempt(s) repaired" if turn.ok else "Attempts"):
                    for a in failed:
                        st.code(a.sql, language="sql")
                        st.caption(f"Error: {a.error}")
            st.caption(f"{turn.latency_s:.1f}s · {len(turn.attempts)} attempt(s)")

    if question := st.chat_input("Ask a question about the music store…"):
        with st.spinner("Writing and running SQL…"):
            try:
                st.session_state.turns.append(agent.ask(question))
            except Exception as exc:  # network / provider errors
                st.error(f"LLM request failed: {exc}")
        st.rerun()
