"""Run the eval set against the real models and score retrieval and answers.

Usage (inside the api container):
    python -m evals.run_eval --ingest          # upload data/ docs first if missing
    python -m evals.run_eval --limit 5         # quick smoke run

Exits with code 1 if retrieval hit rate or answer correctness is below the threshold,
so it can be used as a regression gate in CI.
"""

import argparse
import json
import sys
import time
from pathlib import Path

from sqlalchemy import select

from app import llm, rag
from app.db import SessionLocal, init_db
from app.models import Document

ROOT = Path(__file__).resolve().parent.parent
EVAL_SET = Path(__file__).with_name("eval_set.json")
RESULTS = Path(__file__).with_name("results.json")


def keyword_hit(answer: str, keywords: list[str]) -> bool:
    """Every keyword must appear (case-insensitive). 'a|b' means a OR b is enough."""
    text = answer.lower()
    return all(any(alt.lower() in text for alt in kw.split("|")) for kw in keywords)


def ingest_missing(db) -> None:
    have = set(db.scalars(select(Document.filename)))
    for path in sorted((ROOT / "data").glob("*.md")):
        if path.name == "README.md" or path.name in have:
            continue
        print(f"ingesting {path.name}")
        rag.ingest_document(db, path.name, path.read_text())


def ask_with_backoff(db, question: str, waits=(30, 60)):
    """Free tier: on a rate-limit error, wait and try again (twice at most)."""
    for wait in (*waits, None):
        try:
            return rag.answer_question(db, question)
        except (rag.EmbeddingError, llm.LLMError) as exc:
            limited = "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc)
            if not limited or wait is None:
                raise
            print(f"   rate limited, waiting {wait}s ...")
            time.sleep(wait)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest", action="store_true", help="upload data/*.md that are not stored yet")
    parser.add_argument("--delay", type=float, default=6.0, help="seconds between questions (rate limits)")
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--limit", type=int, default=None, help="only run the first N questions")
    args = parser.parse_args()

    init_db()
    items = json.loads(EVAL_SET.read_text())[: args.limit]
    rows = []

    with SessionLocal() as db:
        if args.ingest:
            ingest_missing(db)

        for i, item in enumerate(items):
            if i:
                time.sleep(args.delay)
            row = {"id": item["id"], "type": item["type"], "question": item["question"]}
            try:
                answer, retrieved = ask_with_backoff(db, item["question"])
                found = [c.filename for c in retrieved]
                row["answer"] = answer.answer
                row["confident"] = answer.confident
                row["retrieved"] = found
                if item["type"] == "rag":
                    row["retrieval_hit"] = any(s in found for s in item["expected_sources"])
                if item["type"] == "negative":
                    row["correct"] = not answer.confident and not answer.sources
                else:
                    row["correct"] = keyword_hit(answer.answer, item["keywords"])
            except Exception as exc:
                row["error"] = str(exc)[:200]
                row["correct"] = False
                if item["type"] == "rag":
                    row["retrieval_hit"] = False

            mark = lambda b: "-" if b is None else ("ok" if b else "FAIL")  # noqa: E731
            print(f"[{item['id']:>2}] {item['type']:<8} retrieval={mark(row.get('retrieval_hit')):<4} "
                  f"answer={mark(row['correct']):<4} {item['question'][:60]}")
            if not row["correct"]:
                preview = (row.get("error") or row.get("answer", "")).replace("\n", " ")
                print(f"     -> {preview[:150]}")
            rows.append(row)

    rag_rows = [r for r in rows if "retrieval_hit" in r]
    hit_rate = sum(r["retrieval_hit"] for r in rag_rows) / max(len(rag_rows), 1)
    correctness = sum(r["correct"] for r in rows) / max(len(rows), 1)

    print("\n" + "=" * 60)
    print(f"Retrieval hit rate (top-5): {hit_rate:6.1%}  ({sum(r['retrieval_hit'] for r in rag_rows)}/{len(rag_rows)})")
    print(f"Answer correctness:         {correctness:6.1%}  ({sum(r['correct'] for r in rows)}/{len(rows)})")
    RESULTS.write_text(json.dumps({"hit_rate": hit_rate, "correctness": correctness, "rows": rows}, indent=2))
    print(f"Details written to {RESULTS.relative_to(ROOT)}")

    if hit_rate < args.threshold or correctness < args.threshold:
        print(f"FAIL: a score is below {args.threshold:.0%}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
