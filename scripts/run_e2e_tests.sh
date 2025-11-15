#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Konfig End-to-End Test Suite${NC}"
echo -e "${YELLOW}========================================${NC}"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Function to cleanup
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Trap to ensure cleanup runs on exit
trap cleanup EXIT

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 1: Stopping any existing containers...${NC}"
docker-compose down -v 2>/dev/null || true
echo -e "${GREEN}✓ Existing containers stopped${NC}"

echo -e "\n${YELLOW}Step 2: Building Docker images...${NC}"
docker-compose build
echo -e "${GREEN}✓ Docker images built${NC}"

echo -e "\n${YELLOW}Step 3: Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"

echo -e "\n${YELLOW}Step 4: Waiting for services to be healthy...${NC}"
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker-compose ps | grep -q "healthy"; then
        # Check if all critical services are healthy
        postgres_health=$(docker-compose ps postgres | grep -c "healthy" || echo "0")
        redis_health=$(docker-compose ps redis | grep -c "healthy" || echo "0")

        if [ "$postgres_health" -eq "1" ] && [ "$redis_health" -eq "1" ]; then
            echo -e "${GREEN}✓ All services are healthy${NC}"
            break
        fi
    fi

    attempt=$((attempt + 1))
    echo -e "  Waiting for services... ($attempt/$max_attempts)"
    sleep 2

    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}✗ Services did not become healthy in time${NC}"
        echo -e "\n${YELLOW}Service Status:${NC}"
        docker-compose ps
        echo -e "\n${YELLOW}Backend Logs:${NC}"
        docker-compose logs backend
        exit 1
    fi
done

echo -e "\n${YELLOW}Step 5: Running database migrations...${NC}"
docker-compose exec -T backend alembic upgrade head
echo -e "${GREEN}✓ Database migrations complete${NC}"

echo -e "\n${YELLOW}Step 6: Waiting for API to be ready...${NC}"
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is ready${NC}"
        break
    fi

    attempt=$((attempt + 1))
    echo -e "  Waiting for API... ($attempt/$max_attempts)"
    sleep 2

    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}✗ API did not become ready in time${NC}"
        echo -e "\n${YELLOW}Backend Logs:${NC}"
        docker-compose logs backend
        exit 1
    fi
done

echo -e "\n${YELLOW}Step 7: Running end-to-end tests...${NC}"
cd backend

# Install test dependencies if not already installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip install pytest pytest-asyncio requests
fi

# Run E2E tests
if python -m pytest tests/test_e2e.py -v -s; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ All E2E tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    TEST_EXIT_CODE=0
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  ✗ Some E2E tests failed${NC}"
    echo -e "${RED}========================================${NC}"
    TEST_EXIT_CODE=1
fi

echo -e "\n${YELLOW}Service logs (last 50 lines):${NC}"
docker-compose logs --tail=50

exit $TEST_EXIT_CODE
