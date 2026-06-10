"""Utility functions for QueryMind."""

from langchain_community.utilities import SQLDatabase

def format_query_result(result):
    """Format the result from SQL execution for display."""
    return result

def extract_sql_from_agent_trace(trace):
    """Extract the SQL query from agent trace."""
    # Parse the agent's internal trace to extract the SQL
    if "SELECT" in str(trace):
        return str(trace)
    return None

def validate_query_safety(query):
    """Ensure query is read-only (no INSERT, UPDATE, DELETE)."""
    dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]
    query_upper = query.upper()
    return not any(keyword in query_upper for keyword in dangerous_keywords)
