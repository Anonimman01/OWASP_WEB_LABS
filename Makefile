# Shortcuts for working with the labs. Run `make help` to see them.
# Lab IDs are the A01..A10 prefixes of the folder names, e.g. `make up LAB=A05`.

LAB      ?=
LAB_DIR  := $(firstword $(wildcard $(LAB)-*))
LABS     := $(sort $(wildcard A[0-9][0-9]-*))

.PHONY: help up down up-all down-all test check

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-9s %s\n", $$1, $$2}'
	@echo
	@echo "  Examples: make up LAB=A05   |   make test   |   make up-all"

up: ## Start one lab in the foreground (needs LAB=A01..A10)
	@test -n "$(LAB)" -a -n "$(LAB_DIR)" || { echo "Usage: make up LAB=A05  (A01..A10)"; exit 1; }
	cd $(LAB_DIR) && docker compose up --build

down: ## Stop one lab (needs LAB=A01..A10)
	@test -n "$(LAB)" -a -n "$(LAB_DIR)" || { echo "Usage: make down LAB=A05  (A01..A10)"; exit 1; }
	cd $(LAB_DIR) && docker compose down

up-all: ## Start all 10 labs in the background (20 containers, ports 8001-8092)
	@for d in $(LABS); do (cd $$d && docker compose up --build -d) || exit 1; done

down-all: ## Stop all labs
	@for d in $(LABS); do (cd $$d && docker compose down); done

test: ## Run the exploit tests (needs: pip install -r requirements-dev.txt)
	python -m pytest

check: ## Run the repo consistency checks used by CI
	python .github/scripts/check_repo.py
