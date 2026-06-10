# ⚡ QueryMind Quick Start

## 30 Second Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env and add your API key
# OPENAI_API_KEY=sk-xxx... (or GROQ_API_KEY=xxx...)

# 3. Install dependencies (optional - see below)
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

---

## What You Get

✅ **Natural Language Queries** — Ask questions in plain English  
✅ **Automatic SQL Generation** — LLM writes SQL for you  
✅ **Smart Retry Logic** — Fixes broken queries automatically  
✅ **Query Transparency** — See the exact SQL used  
✅ **Conversation Memory** — Follow-up questions work  
✅ **Sample Database** — Pre-loaded music store dataset  

---

## Example Questions

- "Which artist generated the most revenue?"
- "Top 5 customers by total spending?"
- "How many tracks are longer than 5 minutes?"
- "Which employee has the most customers?"
- "Show me the genre with the most albums"

---

## Architecture

```
User Question
    ↓
LLM reads schema
    ↓
LLM writes SQL
    ↓
Execute SQL
    ↓
Format answer + show SQL
```

If SQL fails → LLM sees error → retries (up to 3x)

---

## Tech Stack

| Component | Tech |
|-----------|------|
| **UI** | Streamlit |
| **Agent** | LangChain |
| **LLM** | OpenAI GPT-4o or Groq Llama 3.3 70B |
| **Database** | SQLite (Chinook) |

---

## Files Created

```
querymind/
├── app.py                    # Main Streamlit app
├── agent.py                  # LangChain SQL agent
├── utils.py                  # Helper functions
├── setup_db.py              # Database initialization
├── verify_setup.py          # Setup verification
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .gitignore               # Git rules
├── CONFIG.md                # Configuration guide
├── DEPLOYMENT.md            # HuggingFace Spaces guide
├── DEVELOPMENT.md           # Dev setup guide
├── .streamlit/config.toml   # Streamlit config
├── database/
│   └── chinook.db          # SQLite database (52KB)
└── README.md                # Full documentation
```

---

## Troubleshooting

**"API key not found"**
- Edit `.env` and add `OPENAI_API_KEY` or `GROQ_API_KEY`

**"No module named 'streamlit'"**
- Run: `pip install -r requirements.txt`

**"Database not found"**
- Run: `python setup_db.py`

---

## Next Steps

1. ✅ Setup complete
2. 🔑 Add API key to `.env`
3. 🚀 Run `streamlit run app.py`
4. 🎯 Ask your first question!

---

**Ready to go?** Your QueryMind instance is ready to use! 🧠
