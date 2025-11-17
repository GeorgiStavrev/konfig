.PHONY: help install dev clean test test-cov lint format run dev-up dev-down dev-logs dev-status migrate migration-create migration-amend migration-downgrade migration-history db-upgrade db-downgrade db-current docker-up docker-down docker-logs pre-commit-install pre-commit-run security ci

# Variables
VENV := ../venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
ALEMBIC := $(VENV)/bin/alembic
UVICORN := $(VENV)/bin/uvicorn
BLACK := $(VENV)/bin/black
FLAKE8 := $(VENV)/bin/flake8
ISORT := $(VENV)/bin/isort
BANDIT := $(VENV)/bin/bandit
PRE_COMMIT := $(VENV)/bin/pre-commit

# Default target
help:
	@echo "Konfig Backend - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make dev              - Install dev dependencies"
	@echo "  make clean            - Clean Python cache files"
	@echo ""
	@echo "Local Development Commands:"
	@echo "  make dev-up           - Start PostgreSQL & Redis (for local development)"
	@echo "  make dev-down         - Stop PostgreSQL & Redis"
	@echo "  make dev-logs         - View database logs"
	@echo "  make dev-status       - Check if services are running"
	@echo "  make run              - Run the FastAPI server locally (with hot reload)"
	@echo ""
	@echo "Testing & Quality Commands:"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage"
	@echo "  make lint             - Run flake8 linter"
	@echo "  make format           - Format code with black"
	@echo "  make security         - Run security checks (bandit, safety)"
	@echo "  make ci               - Run all CI checks (lint, test, security)"
	@echo ""
	@echo "Pre-commit Commands:"
	@echo "  make pre-commit-install  - Install pre-commit hooks"
	@echo "  make pre-commit-run      - Run pre-commit on all files"
	@echo ""
	@echo "Database Migration Commands:"
	@echo "  make migration-create MSG='description'  - Create new migration"
	@echo "  make migration-amend                     - Amend the last migration"
	@echo "  make db-upgrade                          - Run migrations (upgrade to head)"
	@echo "  make db-downgrade                        - Downgrade one migration"
	@echo "  make db-current                          - Show current migration"
	@echo "  make migration-history                   - Show migration history"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up        - Start docker containers"
	@echo "  make docker-down      - Stop docker containers"
	@echo "  make docker-logs      - View docker logs"

# Setup commands
install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -r requirements-dev.txt 2>/dev/null || $(PIP) install pytest pytest-asyncio pytest-cov black flake8

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true

# Development commands
run:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTEST) tests/ -v

test-cov:
	$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term -v

lint:
	$(FLAKE8) app/ tests/ --max-line-length=120 --exclude=__pycache__,.venv,venv,alembic

format:
	$(BLACK) app/ tests/ --line-length=88

# Pre-commit commands
pre-commit-install:
	$(PRE_COMMIT) install
	@echo "Pre-commit hooks installed successfully"

pre-commit-run:
	$(PRE_COMMIT) run --all-files

# Security commands
security:
	@echo "Running security checks..."
	@echo "\n=== Bandit Security Scan ==="
	-$(BANDIT) -r app/ -ll || true
	@echo "\n=== Safety Dependency Check ==="
	-$(VENV)/bin/safety check || true

# CI command (runs all checks like GitHub Actions)
ci:
	@echo "Running all CI checks..."
	@echo "\n=== Linting with flake8 ==="
	$(FLAKE8) app/ tests/ --max-line-length=120 --exclude=__pycache__,.venv,venv,alembic
	@echo "\n=== Checking code format with black ==="
	$(BLACK) --check app/ tests/ --line-length=88
	@echo "\n=== Checking imports with isort ==="
	$(ISORT) --check-only app/ tests/ --profile black
	@echo "\n=== Running tests with coverage ==="
	$(PYTEST) tests/ --cov=app --cov-report=term -v
	@echo "\n=== Security checks ==="
	-$(BANDIT) -r app/ -ll || true
	@echo "\n✓ All CI checks complete!"

# Database migration commands
migration-create:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG is required. Usage: make migration-create MSG='your message'"; \
		exit 1; \
	fi
	$(ALEMBIC) revision --autogenerate -m "$(MSG)"

migration-amend:
	@echo "Amending last migration..."
	@LAST_MIGRATION=$$($(ALEMBIC) history | grep -E "^[a-f0-9]+ ->" | head -n 1 | awk '{print $$1}'); \
	if [ -z "$$LAST_MIGRATION" ]; then \
		echo "Error: No migrations found"; \
		exit 1; \
	fi; \
	MIGRATION_FILE=$$(find alembic/versions -name "$${LAST_MIGRATION}_*.py" | head -n 1); \
	if [ -z "$$MIGRATION_FILE" ]; then \
		echo "Error: Migration file not found for revision $$LAST_MIGRATION"; \
		exit 1; \
	fi; \
	echo "Found migration: $$MIGRATION_FILE"; \
	echo "Downgrading to previous version..."; \
	$(ALEMBIC) downgrade -1; \
	echo "Deleting migration file..."; \
	rm "$$MIGRATION_FILE"; \
	echo "Migration file deleted. You can now create a new migration with:"; \
	echo "  make migration-create MSG='your message'"

db-upgrade:
	$(ALEMBIC) upgrade head

db-downgrade:
	$(ALEMBIC) downgrade -1

db-current:
	$(ALEMBIC) current

migration-history:
	$(ALEMBIC) history --verbose

# Local development commands (run DB in Docker, backend on host)
dev-up:
	@echo "Starting PostgreSQL and Redis for local development..."
	cd .. && docker-compose -f docker-compose.dev.yml up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "  PostgreSQL: localhost:5433"
	@echo "  Redis: localhost:6379"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run migrations: make db-upgrade"
	@echo "  2. Start the backend: make run"
	@echo "  3. Or debug in VSCode: Press F5"

dev-down:
	@echo "Stopping PostgreSQL and Redis..."
	cd .. && docker-compose -f docker-compose.dev.yml down

dev-logs:
	cd .. && docker-compose -f docker-compose.dev.yml logs -f

dev-status:
	@echo "Checking service status..."
	@cd .. && docker-compose -f docker-compose.dev.yml ps

# Docker commands (full stack)
docker-up:
	cd .. && docker-compose up -d

docker-down:
	cd .. && docker-compose down

docker-logs:
	cd .. && docker-compose logs -f
