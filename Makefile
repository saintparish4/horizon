.PHONY: install db migrate dev test lint typecheck fmt check bench bench-repeat chart similarity similarity-openai metrics

install:
	uv venv --python 3.12
	uv pip install -e ".[dev]"

# Local Postgres 16 + pgvector, no Docker required. Prints the DATABASE_URL.
db:
	.venv/bin/python -m horizon.devdb

migrate:
	.venv/bin/alembic upgrade head

dev:
	.venv/bin/uvicorn horizon.main:app --reload --port 8000

test:
	.venv/bin/python -m pytest tests/ -q

lint:
	.venv/bin/ruff check horizon tests migrations benchmarks scripts
	.venv/bin/ruff format --check horizon tests migrations benchmarks scripts

typecheck:
	.venv/bin/mypy horizon

fmt:
	.venv/bin/ruff format horizon tests migrations benchmarks scripts
	.venv/bin/ruff check --fix horizon tests migrations benchmarks scripts

bench:
	.venv/bin/python -m benchmarks.run --tasks 1000 --seed 42

chart:
	.venv/bin/python -m benchmarks.chart

# Spread across 5 seeds. The engine is not bit-reproducible (HNSW search is
# approximate), so a single seed overstates how exact the headline number is.
bench-repeat:
	.venv/bin/python -m benchmarks.run --tasks 1000 --seed 42 --repeat 5

# Where should EVIDENCE_MIN_SIMILARITY sit? Measures it instead of guessing.
similarity:
	.venv/bin/python -m benchmarks.similarity --phrasing template
	.venv/bin/python -m benchmarks.similarity --phrasing paraphrase

# The measurement that actually decides the threshold. Needs OPENAI_API_KEY and
# spends a few cents; until it runs, 0.75 is a guess carried over from lexical
# embeddings whose similarity scores live in a completely different range.
similarity-openai:
	.venv/bin/python -m benchmarks.similarity --embeddings openai --phrasing template
	.venv/bin/python -m benchmarks.similarity --embeddings openai --phrasing paraphrase

metrics:
	.venv/bin/python -m scripts.metrics

check: lint typecheck test
