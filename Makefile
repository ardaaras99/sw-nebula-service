PROJECT_NAME:=sw_nebula_service
EXECUTER:=uv run

all: format lint test

init:
	git init
	$(EXECUTER) uv sync
	$(EXECUTER) pre-commit install

clean:
	rm -rf .mypy_cache .pytest_cache .coverage htmlcov
	$(EXECUTER) ruff clean

format:
	$(EXECUTER) ruff format .

lint:
	$(EXECUTER) ruff check . --fix

test:
	$(EXECUTER) pytest --cov-report term-missing --cov-report html --cov $(PROJECT_NAME)/





