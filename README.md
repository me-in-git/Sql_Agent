# QueryMind

Ask questions about a SQL database in plain English. An LLM writes the query, it runs read-only
against SQLite, and you get the answer along with the SQL and the result table.

Uses the [Chinook](https://github.com/lerocha/chinook-database) music store database (11 tables, ~15k rows).

## How it works

1. The model gets the schema, a couple of sample rows per table, and the last few questions with their SQL,
   so follow-ups like "and for Canada?" work.
2. The SQL runs against the database opened read-only. A SQLite authorizer only allows reads, and long
   queries are cut off by a timeout.
3. If the query fails, the error goes back to the model to fix (up to 3 tries).
4. The model writes a short answer from the result rows.

## Results

`eval/questions.json` has 40 questions with hand-written gold SQL: 10 each of easy, medium, hard and
"expert" (window functions, recursive CTEs, year-over-year growth). An answer counts if its result matches
the gold result.

| model (Groq) | accuracy | expert |
|---|---|---|
| gpt-oss-120b | 40/40 | 10/10 |
| qwen3.8-27b | 38/40 | 8/10 |

Both Qwen misses were the same mistake: counting rows inside each group instead of counting the groups.

```bash
python -m eval.run_eval --out results.json
```

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env      # add GROQ_API_KEY (or OPENAI_API_KEY)
streamlit run app.py
pytest                    # no API key needed
```

## Notes

- Putting the whole schema in the prompt works for 11 tables; a bigger database would need to pick
  relevant tables first.
- 40 questions is a small benchmark.

Chinook database © Luis Rocha (see `database/CHINOOK_LICENSE.md`).
