.PHONY: run dev test smoke

run:
	PYTHONPATH=src uv run uvicorn splitpost.main:app --port 8000

dev:
	PYTHONPATH=src uv run uvicorn splitpost.main:app --port 8000 --reload

test:
	PYTHONPATH=src uv run python -m pytest tests/ -v

smoke:
	PYTHONPATH=src uv run python smoke_test.py
