.PHONY: help install dev clean test test-cov lint format run migrate migration-create migration-amend migration-downgrade migration-history db-upgrade db-downgrade db-current docker-up docker-down docker-logs

# Variables
VENV := ../venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
ALEMBIC := $(VENV)/bin/alembic
UVICORN := $(VENV)/bin/uvicorn
BLACK := $(VENV)/bin/black
FLAKE8 := $(VENV)/bin/flake8

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
	@echo "Development Commands:"
	@echo "  make run              - Run the FastAPI server"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage"
	@echo "  make lint             - Run flake8 linter"
	@echo "  make format           - Format code with black"
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

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
