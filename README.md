# QueryMind 
### Natural Language SQL Agent — ask questions, get answers, no SQL required.
---

## What is this?

QueryMind is an agentic SQL system that lets you query a relational database in plain English. Under the hood, an LLM agent inspects the database schema, writes SQL, executes it, and returns a natural language answer — retrying automatically if the query fails.

> **"Which artist generated the most revenue in 2010?"**
> → Agent inspects schema → writes JOIN query → executes → returns answer with the SQL shown.

No SQL knowledge required.

---

## Demo

> Deployed on HuggingFace Spaces: [https://me-in-git-sql-agent-app-imrld8.streamlit.app/]

---

## Features

- **Natural language to SQL** — powered by LangChain's SQL agent + OpenAI/Groq
- **Schema-aware query repair** — if generated SQL fails, the agent retries with the error message as feedback
- **Query transparency** — every answer shows the SQL that produced it
- **Multi-table reasoning** — handles JOINs, aggregations, and nested queries across 11 tables
- **Conversation memory** — maintains context across follow-up questions
- **Chinook database** — ships with a real-world music store dataset (artists, albums, tracks, invoices, customers)

---

## Architecture

```
User Query
    │
    ▼
LangChain SQL Agent
    │
    ├── inspect_schema()        # Lists tables + columns
    ├── generate_sql()          # LLM writes SQL from schema + query
    ├── execute_sql()           # Runs against SQLite
    │       │
    │       └── on failure ──► retry with error feedback 
    │
    └── generate_answer()       # LLM summarizes result in natural language
    │
    ▼
Streamlit UI (query + SQL + answer)
```

---

## Quickstart

```bash
# Clone the repo
git clone https://github.com/your-username/querymind
cd querymind

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Edit .env and add OPENAI_API_KEY or GROQ_API_KEY

# Run
streamlit run app.py
```

---

## Project Structure

```
querymind/
├── app.py               # Streamlit UI
├── agent.py             # LangChain SQL agent setup
├── database/
│   └── chinook.db       # SQLite database (ships with repo)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | LangChain SQL Agent |
| LLM | Groq (llama-3.3-70b) / OpenAI GPT-4o |
| Database | SQLite (Chinook) |
| UI | Streamlit |
| Deployment | HuggingFace Spaces |

---

## Example Queries

```
"Which genre has the most tracks?"
"Top 5 customers by total spending?"
"Which employee has the most customers assigned?"
"What percentage of tracks are longer than 5 minutes?"
"Which album has the highest average track price?"
```

---

## Key Design Decisions

**Schema-aware retry:** If the LLM generates invalid SQL, the agent feeds the SQLite error message back as context and retries (up to 3 times). This handles column name hallucinations and JOIN errors without user intervention.

**SQL transparency:** Every answer surfaces the raw SQL query that produced it. This makes the agent auditable — users can verify correctness without trusting the LLM blindly.

**Groq for speed:** Using Groq's inference API keeps response latency low even for multi-step agent traces.

---

## Limitations

- Read-only queries only (no INSERT/UPDATE/DELETE)
- Works best on well-structured relational databases; unstructured or denormalized schemas degrade performance
- LLM may occasionally hallucinate column names on first attempt — mitigated by retry mechanism

---

## Future Work

- Support for uploaded user databases (CSV → SQLite auto-conversion)
- Query history and export
- Multi-database support (PostgreSQL, MySQL)
- Fine-tuned text-to-SQL model as a faster/cheaper alternative to general LLM
