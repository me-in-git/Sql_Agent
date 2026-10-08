import json
from pathlib import Path

import pytest

from eval.run_eval import evaluate, results_match
from querymind import QueryError, ReadOnlyDatabase, SQLAgent
from querymind.agent import extract_sql

QUESTIONS = json.loads((Path(__file__).parent.parent / "eval" / "questions.json").read_text(encoding="utf-8"))


class ScriptedLLM:
    """Returns canned replies in order and records every prompt it was sent."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.model = "scripted"

    def chat(self, messages):
        self.calls.append(messages)
        return self.replies.pop(0)


@pytest.fixture(scope="module")
def db():
    return ReadOnlyDatabase()


# ---------- read-only enforcement ----------
@pytest.mark.parametrize("sql", [
    "DELETE FROM Artist",
    "UPDATE Track SET UnitPrice = 0",
    "INSERT INTO Genre (GenreId, Name) VALUES (99, 'x')",
    "DROP TABLE Album",
    "CREATE TABLE t (x INT)",
    "ATTACH DATABASE 'other.db' AS other",
    "PRAGMA writable_schema = 1",
    "SELECT 1; DROP TABLE Album",
    "WITH x AS (SELECT 1) DELETE FROM Artist",
])
def test_writes_and_side_effects_are_rejected(db, sql):
    with pytest.raises(QueryError):
        db.run(sql)
    assert db.run("SELECT COUNT(*) FROM Album").rows == [(347,)]


def test_keyword_inside_string_is_not_a_false_positive(db):
    assert db.run("SELECT COUNT(*) FROM Track WHERE Name LIKE '%Drop%'").rows[0][0] >= 0


def test_long_running_query_is_interrupted():
    slow = ReadOnlyDatabase(timeout_s=0.2)
    with pytest.raises(QueryError, match="time limit"):
        slow.run("SELECT COUNT(*) FROM Track a, Track b, Track c")


def test_rows_are_capped():
    capped = ReadOnlyDatabase(max_rows=10)
    result = capped.run("SELECT Name FROM Track")
    assert len(result.rows) == 10 and result.truncated


def test_gold_queries_all_run(db):
    for q in QUESTIONS:
        assert db.run(q["gold"]).rows, q["id"]


# ---------- agent loop ----------
def test_extract_sql_from_code_block():
    assert extract_sql("Here:\n```sql\nSELECT 1;\n```") == "SELECT 1"
    assert extract_sql("SELECT 2") == "SELECT 2"


def test_agent_repairs_a_failing_query(db):
    llm = ScriptedLLM([
        "```sql\nSELECT COUNT(*) FROM Artists\n```",  # wrong table name
        "```sql\nSELECT COUNT(*) FROM Artist\n```",
        "There are 275 artists.",
    ])
    result = SQLAgent(llm, db).ask("How many artists are there?")
    assert result.ok and result.result.rows == [(275,)]
    assert [a.error is not None for a in result.attempts] == [True, False]
    assert "no such table" in llm.calls[1][-1]["content"]
    assert result.answer == "There are 275 artists."


def test_agent_gives_up_after_max_attempts(db):
    llm = ScriptedLLM(["```sql\nDELETE FROM Artist\n```"] * 3)
    result = SQLAgent(llm, db, max_attempts=3).ask("Delete everything")
    assert not result.ok and len(result.attempts) == 3
    assert "read-only" in result.attempts[0].error


def test_follow_up_questions_see_previous_sql(db):
    llm = ScriptedLLM([
        "```sql\nSELECT COUNT(*) FROM Customer WHERE Country = 'Brazil'\n```", "5 customers.",
        "```sql\nSELECT COUNT(*) FROM Customer WHERE Country = 'Canada'\n```", "8 customers.",
    ])
    agent = SQLAgent(llm, db)
    agent.ask("How many customers are from Brazil?")
    agent.ask("And from Canada?")
    follow_up_prompt = llm.calls[2]
    assert any("Brazil" in m["content"] for m in follow_up_prompt if m["role"] == "assistant")


# ---------- evaluation harness ----------
def test_results_match_ignores_order_and_extra_columns():
    gold = [("Rock",), ("Latin",)]
    assert results_match(gold, [("Latin", 382.1), ("Rock", 826.6)])
    assert not results_match(gold, [("Rock",)])
    assert not results_match(gold, [("Rock",), ("Metal",)])
    assert results_match([(2328.6,)], [(2328.6000000001,)])
    # full names split into first/last columns still match
    assert results_match([("Helena Holý",)], [("Helena", "Holý")])
    assert not results_match([("Helena Holý",)], [("Helena", "Smith")])


def test_eval_with_perfect_model_scores_100(db):
    gold_replies = [f"```sql\n{q['gold']}\n```" for q in QUESTIONS]
    report = evaluate(SQLAgent(ScriptedLLM(gold_replies), db), db, QUESTIONS)
    assert report["questions"] == 40
    assert report["execution_accuracy"] == 1.0
