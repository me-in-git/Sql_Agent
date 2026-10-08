"""Execution accuracy on eval/questions.json.

A prediction is correct if its result contains the gold result (row order
ignored, extra columns allowed, numbers rounded to 2 dp).

    python -m eval.run_eval --out results.json

"""

import argparse
import json
import time
from collections import Counter
from itertools import permutations
from pathlib import Path

from dotenv import load_dotenv

from querymind import ReadOnlyDatabase, SQLAgent

QUESTIONS = Path(__file__).with_name("questions.json")


def _norm(v):
    if isinstance(v, float):
        return round(v, 2)
    if isinstance(v, str):
        return v.strip().lower()
    return v


def results_match(gold_rows: list[tuple], pred_rows: list[tuple]) -> bool:
    """True if some choice of predicted columns reproduces the gold rows as a multiset."""
    if len(gold_rows) != len(pred_rows):
        return False
    if not gold_rows:
        return True
    g_width, p_width = len(gold_rows[0]), len(pred_rows[0])
    if p_width < g_width:
        return False
    gold = Counter(tuple(_norm(v) for v in r) for r in gold_rows)
    for cols in permutations(range(p_width), g_width):
        if Counter(tuple(_norm(r[c]) for c in cols) for r in pred_rows) == gold:
            return True
    # full names may come back as separate FirstName, LastName columns
    if g_width == 1 and isinstance(gold_rows[0][0], str):
        joined = Counter((_norm(" ".join(v for v in r if isinstance(v, str))),) for r in pred_rows)
        return joined == gold
    return False


def evaluate(agent: SQLAgent, db: ReadOnlyDatabase, questions: list[dict]) -> dict:
    rows = []
    for q in questions:
        agent.history.clear()  # each question is independent
        gold = db.run(q["gold"]).rows
        t0 = time.perf_counter()
        sql, result, attempts = agent.generate_sql(q["question"])
        correct = result is not None and results_match(gold, result.rows)
        rows.append({
            "id": q["id"], "level": q["level"], "question": q["question"], "correct": correct,
            "attempts": len(attempts), "repaired": len(attempts) > 1 and result is not None,
            "sql": sql, "errors": [a.error for a in attempts if a.error],
            "latency_s": round(time.perf_counter() - t0, 2),
        })
        print(f"[{'PASS' if correct else 'FAIL'}] #{q['id']:>2} {q['level']:<6} attempts={len(attempts)} {q['question']}")

    def acc(subset):
        return round(sum(r["correct"] for r in subset) / len(subset), 3) if subset else None

    by_level = {lvl: acc([r for r in rows if r["level"] == lvl]) for lvl in ("easy", "medium", "hard", "expert")}
    return {
        "model": getattr(agent.llm, "model", "unknown"),
        "execution_accuracy": acc(rows),
        "by_level": by_level,
        "questions": len(rows),
        "needed_repair": sum(r["repaired"] for r in rows),
        "repaired_and_correct": sum(r["repaired"] and r["correct"] for r in rows),
        "failed_to_produce_sql": sum(r["sql"] is None for r in rows),
        "results": rows,
    }


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    from querymind.llm import OpenAICompatibleLLM

    db = ReadOnlyDatabase()
    agent = SQLAgent(OpenAICompatibleLLM(), db, max_attempts=args.max_attempts)
    report = evaluate(agent, db, json.loads(QUESTIONS.read_text(encoding="utf-8")))
    summary = {k: v for k, v in report.items() if k != "results"}
    print(json.dumps(summary, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
