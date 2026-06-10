# QueryMind Configuration

These settings control how QueryMind behaves:

## Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4o
- `GROQ_API_KEY`: Your Groq API key for Llama 3.3 70B (alternative to OpenAI)
- `MODEL`: Default model to use (defaults to gpt-4o)

## Retry Logic
- Max retries: 3 attempts to fix failed SQL queries
- Retry trigger: SQLite error message is fed back to LLM

## Database
- Default: SQLite (Chinook database)
- Location: `database/chinook.db`
- Schema: 11 tables with artist, album, track, customer, invoice, and employee data

## Safety
- Read-only queries only
- No INSERT, UPDATE, DELETE, DROP, ALTER operations allowed
