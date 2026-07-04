# Canonical task runner — `make check` mirrors CI exactly.
.DEFAULT_GOAL := help
FRONTEND := website/frontend
RUFF ?= ruff

help: ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

setup: ## install dev dependencies (frontend; ruff via pipx/pip/venv)
	cd $(FRONTEND) && npm ci --no-fund --no-audit
	@command -v $(RUFF) >/dev/null || echo ">> install ruff: pipx install ruff (or pip install ruff in a venv), or: make RUFF=/path/to/ruff"

check: consistency lint terraform frontend test ## everything CI runs

consistency: ## repo content invariants
	python3 tools/consistency_check.py

lint: ## ruff (py) + prettier (ts/css) checks
	$(RUFF) check .
	$(RUFF) format --check .
	cd $(FRONTEND) && npx prettier --check .

fmt: ## auto-format everything
	$(RUFF) check --fix .
	$(RUFF) format .
	cd $(FRONTEND) && npx prettier --write .
	terraform -chdir=website/terraform fmt -recursive

terraform: ## fmt-check + validate (no backend/AWS)
	terraform -chdir=website/terraform fmt -check -recursive
	terraform -chdir=website/terraform init -backend=false -input=false > /dev/null
	terraform -chdir=website/terraform validate

frontend: ## typecheck + build the chat UI
	cd $(FRONTEND) && npm run build

test: ## backend SSE contract smoke test (no AWS)
	python3 website/backend/test_smoke.py

corpus-dry: ## chunker stats without AWS
	python3 website/scripts/sync_corpus.py --dry-run
	@rm -rf website/scripts/out

drill: ## verifier agent, MC mode (needs Ollama)
	python3 agents/verifier.py

tutor: ## Socratic tutor agent (needs Ollama)
	python3 agents/socratic_tutor.py

.PHONY: help setup check consistency lint fmt terraform frontend test corpus-dry drill tutor
