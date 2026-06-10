"""LangChain SQL Agent setup for QueryMind."""

import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

def create_agent():
    """Initialize and return the SQL agent."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("Neither OPENAI_API_KEY nor GROQ_API_KEY found in .env")
    
    # Initialize LLM
    if os.getenv("GROQ_API_KEY"):
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0
        )
    else:
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o-mini",
            temperature=0
        )
    
    # Connect to Chinook database
    db = SQLDatabase.from_uri("sqlite:///database/chinook.db")
    
    # Create SQL agent
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        max_iterations=20,        
        max_execution_time=30,   
        handle_parsing_errors=True,
            agent_kwargs={ "system_message": """You are a helpful data analyst assistant.
When answering questions:
- Trust the SQL query result completely — that is the ground truth
- Never second-guess the query result based on sample rows shown in the schema
- Answer in one clean sentence e.g. 'There are 275 artists in the database.'
- If listing multiple results, format them clearly
- Never expose your internal reasoning or mention tools, schemas, or observations"""
    }

    )
    
    return agent, db

def get_schema_info(db):
    """Retrieve database schema information."""
    return db.get_table_info()
