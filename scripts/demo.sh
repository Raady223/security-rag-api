#!/usr/bin/env bash
# Scripted walkthrough used to record docs/demo.gif.
# Run from the repo root with a fresh database:  docker compose down -v && ./scripts/demo.sh
set -euo pipefail

say() { printf '\n\033[1;36m# %s\033[0m\n' "$1"; sleep 1; }

run() {  # print the command as if typed, then run it
  printf '\033[1;32m$\033[0m '
  for ((i = 0; i < ${#1}; i++)); do printf '%s' "${1:i:1}"; sleep 0.015; done
  echo; sleep 0.5
  eval "$1"
  sleep 2
}

ask() {
  curl -s localhost:8000/ask -H 'content-type: application/json' \
    -d "{\"question\": \"$1\"}" | jq -C .
}

clear
say "1. Start Postgres + pgvector and the FastAPI service with one command"
run "docker compose up -d --wait 2>/dev/null && curl -s localhost:8000/health | jq -C ."

say "2. Upload 7 security documents: chunk -> embed (Gemini) -> store vectors in pgvector"
run 'for f in data/mitre_*.md data/playbook_*.md; do curl -s -F "file=@$f" localhost:8000/documents; echo; done'

say "3. Ask a question (ask = curl POST /ask): answers only from the documents, citing chunk ids"
run 'ask "What is password spraying and why does it avoid account lockout?"'

say "4. Tool calling: T1003 is in no document, so the model calls get_technique (a SQL lookup)"
run 'ask "What is T1003 and which tactic does it belong to?"'
run "docker compose logs api | grep -o 'tool round.*' | cut -c1-110"

say "5. Off-topic question: refused by the relevance gate, without calling the LLM"
run 'ask "What is a good recipe for banana bread?"'

say "6. Evaluation: retrieval hit rate + answer correctness, fails CI below 80% (first 6 of 28)"
run "docker compose exec api python -m evals.run_eval --limit 6 --delay 4 2>/dev/null"

say "Full 28-question run: 100% top-5 retrieval hit rate, 100% answer correctness"
sleep 3
