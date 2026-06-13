.PHONY: install dev test lint type run finalize clean

install:
	python -m pip install -e .

dev:
	python -m pip install -e ".[dev,serve]"

test:
	python -m pytest -q

lint:
	ruff check .

type:
	mypy

run:
	uvicorn app.api:app --reload --port 8000

finalize:
	@test -n "$(FILE)" || (echo "usage: make finalize FILE=path.md"; exit 2)
	python -m tools.finalizer100 "$(FILE)"

clean:
	rm -rf .pytest_cache **/__pycache__ *.egg-info build dist
