# QueryMind Development Guide

## Project Structure

```
querymind/
├── app.py                 # Streamlit UI entry point
├── agent.py              # LangChain SQL agent configuration
├── utils.py              # Utility functions
├── setup_db.py           # Database initialization script
├── database/
│   └── chinook.db        # SQLite database (auto-generated)
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── README.md             # Main documentation
├── DEPLOYMENT.md         # Deployment instructions
├── CONFIG.md             # Configuration guide
└── DEVELOPMENT.md        # This file
```

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/querymind.git
   cd querymind
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**
   ```bash
   python setup_db.py
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI or Groq API key
   ```

6. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Key Components

### agent.py
- Initializes LangChain's SQL agent
- Handles database connection
- Implements retry logic for failed queries
- Supports both OpenAI and Groq LLMs

### app.py
- Streamlit UI for natural language queries
- Displays query results with SQL transparency
- Maintains conversation history
- Shows example queries

### setup_db.py
- Creates SQLite database with schema
- Populates sample music industry data
- Runs once during initial setup

## Adding New Databases

To support additional databases:

1. Update `agent.py` with new database connection
2. Modify `create_agent()` to accept database parameter
3. Update `.env` with new database credentials

## Testing Queries

Example questions to test:
- "How many tracks are there?"
- "Which artist has the most albums?"
- "What is the total revenue from all invoices?"
- "Which customer spent the most money?"
- "Show me the top 5 longest tracks"

## Troubleshooting

**API Key Issues**
- Verify OPENAI_API_KEY or GROQ_API_KEY is set in .env
- Check that the key has appropriate permissions

**Database Errors**
- Run `python setup_db.py` to recreate the database
- Check file permissions on `database/chinook.db`

**LLM Response Issues**
- Try a different query phrasing
- Check that database schema is correct
- Review agent trace in Streamlit app (verbose mode)

## Performance Tips

- Use Groq for faster inference (cheaper and lower latency)
- Limit conversation history to recent queries
- Pre-compute common aggregations if needed
- Consider query caching for repeated questions
