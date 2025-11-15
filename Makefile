# Virtual environment settings
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
UVICORN := $(VENV)/bin/uvicorn
ALEMBIC := $(VENV)/bin/alembic

.PHONY: help venv install install-dev dev test clean docker-up docker-down docker-logs migrate init-db clean-venv

help:
	@echo "Konfig - Configuration as a Service"
	@echo ""
	@echo "Available commands:"
	@echo "  make venv         - Create virtual environment"
	@echo "  make install      - Install dependencies in virtual environment"
	@echo "  make install-dev  - Install dev dependencies in virtual environment"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker logs"
	@echo "  make migrate      - Run database migrations"
	@echo "  make init-db      - Initialize database"
	@echo "  make clean        - Clean up temporary files"
	@echo "  make clean-venv   - Remove virtual environment"

venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV); \
		echo "Virtual environment created at ./$(VENV)"; \
	else \
		echo "Virtual environment already exists at ./$(VENV)"; \
	fi

install: venv
	@echo "Installing dependencies in virtual environment..."
	cd backend && ../$(PIP) install -r requirements.txt
	@echo "Dependencies installed successfully!"

install-dev: venv
	@echo "Installing dev dependencies in virtual environment..."
	cd backend && ../$(PIP) install -r requirements-dev.txt
	@echo "Dev dependencies installed successfully!"

dev: venv
	@if [ ! -f "$(UVICORN)" ]; then \
		echo "Dependencies not installed. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	cd backend && ../$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

test: venv
	@if [ ! -f "$(PYTEST)" ]; then \
		echo "Dependencies not installed. Running 'make install-dev' first..."; \
		$(MAKE) install-dev; \
	fi
	cd backend && ../$(PYTEST)

docker-up:
	docker-compose up -d

docker-up-rebuild:
	docker-compose up -d --build --force-recreate

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

migrate: venv
	@if [ ! -f "$(ALEMBIC)" ]; then \
		echo "Dependencies not installed. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	cd backend && ../$(ALEMBIC) upgrade head

init-db: venv
	@if [ ! -f "$(PYTHON)" ]; then \
		echo "Dependencies not installed. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	cd backend && ../$(PYTHON) scripts/init_db.py

clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

clean-venv:
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "Virtual environment removed!"
