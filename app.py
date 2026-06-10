"""Streamlit app for QueryMind - Natural Language SQL Agent."""

import streamlit as st
import os
from dotenv import load_dotenv
from agent import create_agent, get_schema_info

load_dotenv()

st.set_page_config(
    page_title="QueryMind",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 QueryMind")
st.markdown("**Natural Language SQL Agent** — Ask questions, get answers. No SQL required.")

# Check for API key first
if not os.getenv("OPENAI_API_KEY") and not os.getenv("GROQ_API_KEY"):
    st.warning("**API Key Required**")
    st.markdown("""
    Please configure your API key to use QueryMind:
    
    1. Copy the environment file:
       ```bash
       cp .env.example .env
       ```
    
    2. Edit `.env` and add ONE of:
       ```
       OPENAI_API_KEY=sk-your-key-here
       # or
       GROQ_API_KEY=your-groq-key-here
       ```
    
    3. Save the file and refresh this page
    
    **Get API Keys:**
    - [OpenAI API Key](https://platform.openai.com/api-keys) (Paid)
    - [Groq API Key](https://console.groq.com) (FREE!)
    """)
    st.stop()

# Initialize session state
if "agent" not in st.session_state:
    try:
        st.session_state.agent, st.session_state.db = create_agent()
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.info("Make sure your API key is set in the .env file and try refreshing the page.")
        st.stop()

# Sidebar with database info
with st.sidebar:
    st.header(" Database Info")
    if st.session_state.db:
        st.write("**Tables:**")
        tables = st.session_state.db.get_usable_table_names()
        for table in tables:
            st.write(f"• {table}")

# Main interface
st.header("Ask Your Question")

user_query = st.text_input(
    "What would you like to know?",
    placeholder="e.g., Which artist generated the most revenue in 2010?"
)

col1, col2 = st.columns([3, 1])

with col2:
    submit_button = st.button("🔍 Search", use_container_width=True)

if submit_button and user_query:
    with st.spinner("Thinking..."):
        try:
            result = st.session_state.agent.invoke({"input": user_query})
            
            # Handle result format
            if isinstance(result, dict):
                answer = result.get("output", str(result))
            else:
                answer = str(result)
            
            # Display result
            st.success("✅ Query executed successfully")
            
            st.subheader("📝 Answer")
            st.write(answer)
            
            # Store in conversation memory
            st.session_state.messages.append({
                "query": user_query,
                "answer": answer
            })
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"Error: {error_msg}")
            if "max iterations" in error_msg.lower():
                st.info("💡 The query was complex. Try a simpler question or check your database schema.")

# Display conversation history
if st.session_state.messages:
    st.header("💬 Conversation History")
    for i, msg in enumerate(st.session_state.messages):
        with st.expander(f"Q{i+1}: {msg['query'][:50]}..."):
            st.write(f"**Question:** {msg['query']}")
            st.write(f"**Answer:** {msg['answer']}")

# Example queries section
with st.expander("💡 Example Queries"):
    st.markdown("""
    - "Which genre has the most tracks?"
    - "Top 5 customers by total spending?"
    - "Which employee has the most customers assigned?"
    - "What percentage of tracks are longer than 5 minutes?"
    - "Which album has the highest average track price?"
    """)

st.divider()
st.caption("Powered by LangChain, OpenAI/Groq, and SQLite")
