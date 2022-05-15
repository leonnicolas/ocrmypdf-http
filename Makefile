.PHONY: run lint check-lint install

SRC := $(shell find . -type f -name "*.py")

api.yaml: $(SRC)
	poetry run python print_openapi.py > $@

run:
	poetry run python main.py

lint:
	poetry run black .

check-lint:
	poetry run black --check .

install:
	poetry install
