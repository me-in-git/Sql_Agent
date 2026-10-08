"""Text-to-SQL loop: generate SQL, run it read-only, retry with the error on failure, answer."""

import re
import time
from dataclasses import dataclass, field

from .db import QueryError, QueryResult, ReadOnlyDatabase
from .llm import LLM

SYSTEM_PROMPT = """You translate questions into SQLite queries for the database below.

Rules:
- Return exactly one read-only SELECT statement (CTEs allowed) inside a ```sql code block.
- Use only tables and columns that exist in the schema. Quote nothing unnecessarily.
- Dates are stored as text 'YYYY-MM-DD HH:MM:SS'; use strftime() or substr() for years/months.
- Revenue is SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) unless invoice totals are asked for.
- For "top N" questions use ORDER BY ... LIMIT N.
- Do not explain; output only the code block.

Schema:
{schema}
"""

ANSWER_PROMPT = """Question: {question}
SQL: {sql}
Result columns: {columns}
Result rows (first {n} of {total}{more}):
{rows}

Answer the question in one or two plain sentences using only these results.
If the result is empty, say that no matching data was found."""

_SQL_BLOCK = re.compile(r"```(?:sql)?\s*(.*?)```", re.S | re.I)


def extract_sql(text: str) -> str:
    m = _SQL_BLOCK.search(text)
    return (m.group(1) if m else text).strip().rstrip(";").strip()


@dataclass
class Attempt:
    sql: str
    error: str | None = None


@dataclass
class AgentResult:
    question: str
    sql: str | None
    result: QueryResult | None
    answer: str
    attempts: list[Attempt] = field(default_factory=list)
    latency_s: float = 0.0

    @property
    def ok(self) -> bool:
        return self.result is not None


class SQLAgent:
    def __init__(self, llm: LLM, db: ReadOnlyDatabase, max_attempts: int = 3, history_turns: int = 3):
        self.llm = llm
        self.db = db
        self.max_attempts = max_attempts
        self.history_turns = history_turns
        self._system = SYSTEM_PROMPT.format(schema=db.schema())
        self.history: list[tuple[str, str]] = []  # (question, sql) for follow-up questions

    def generate_sql(self, question: str) -> tuple[str | None, QueryResult | None, list[Attempt]]:
        messages = [{"role": "system", "content": self._system}]
        for q, s in self.history[-self.history_turns:]:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": f"```sql\n{s}\n```"})
        messages.append({"role": "user", "content": question})

        attempts: list[Attempt] = []
        for _ in range(self.max_attempts):
            reply = self.llm.chat(messages)
            sql = extract_sql(reply)
            try:
                result = self.db.run(sql)
            except QueryError as exc:
                attempts.append(Attempt(sql, str(exc)))
                messages.append({"role": "assistant", "content": reply})
                messages.append({
                    "role": "user",
                    "content": f"That query failed with: {exc}\nReturn a corrected query in a ```sql block.",
                })
                continue
            attempts.append(Attempt(sql))
            return sql, result, attempts
        return None, None, attempts

    def ask(self, question: str) -> AgentResult:
        t0 = time.perf_counter()
        sql, result, attempts = self.generate_sql(question)
        if result is None:
            answer = f"I couldn't produce a working query after {len(attempts)} attempts."
            return AgentResult(question, None, None, answer, attempts, time.perf_counter() - t0)

        self.history.append((question, sql))
        shown = result.rows[:30]
        answer = self.llm.chat([{
            "role": "user",
            "content": ANSWER_PROMPT.format(
                question=question, sql=sql, columns=", ".join(result.columns),
                n=len(shown), total=len(result.rows), more="+" if result.truncated else "",
                rows="\n".join(" | ".join(str(v) for v in r) for r in shown) or "(no rows)",
            ),
        }]).strip()
        return AgentResult(question, sql, result, answer, attempts, time.perf_counter() - t0)
