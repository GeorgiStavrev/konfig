# Konfig Testing Guide

## Test Suite Overview

Konfig includes a comprehensive test suite with three levels of testing:

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test API endpoints and database interactions
3. **End-to-End Tests** - Test the entire application with real HTTP requests

## Test Files

### Unit Tests

#### `tests/test_security.py`
Tests for security utilities including:
- Password hashing and verification
- JWT token creation and decoding
- Data encryption and decryption
- Unicode and edge case handling

#### `tests/test_auth.py`
Tests for authentication endpoints:
- Tenant registration
- Login and token generation
- Duplicate email handling
- Invalid credential handling

### Integration Tests

#### `tests/test_namespaces.py`
Tests for namespace management:
- Create, read, update, delete operations
- Namespace listing
- Multi-tenant isolation
- Authorization checks

#### `tests/test_configs.py`
Tests for configuration management:
- All configuration types (string, number, select, JSON)
- Secret configuration handling
- Configuration versioning and history
- Encryption at rest
- Multi-tenant isolation
- Duplicate key prevention

### End-to-End Tests

#### `tests/test_e2e.py`
Comprehensive E2E tests that run against a live instance:
- Health check endpoint
- Complete authentication flow
- Namespace CRUD operations
- Configuration CRUD operations
- All configuration types
- Version history tracking
- Secret handling
- Multi-tenant data isolation

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx requests
```

### Running Unit and Integration Tests

Run all tests except E2E:
```bash
cd backend
pytest tests/ --ignore=tests/test_e2e.py -v
```

Run with coverage:
```bash
cd backend
pytest tests/ --ignore=tests/test_e2e.py -v --cov=app --cov-report=html
```

Run specific test files:
```bash
# Security tests
pytest tests/test_security.py -v

# Authentication tests
pytest tests/test_auth.py -v

# Namespace tests
pytest tests/test_namespaces.py -v

# Configuration tests
pytest tests/test_configs.py -v
```

### Running End-to-End Tests

E2E tests require a running instance of the application.

#### Option 1: Using the automated script

```bash
cd /Users/georgistavrev/projs/konfig
bash scripts/run_e2e_tests.sh
```

This script will:
1. Stop any existing containers
2. Build Docker images
3. Start all services (PostgreSQL, Redis, Backend)
4. Wait for services to be healthy
5. Run database migrations
6. Execute E2E tests
7. Clean up containers

#### Option 2: Manual execution

1. Start Docker Desktop

2. Start services:
```bash
cd /Users/georgistavrev/projs/konfig
docker-compose up -d
```

3. Wait for services to be ready:
```bash
# Check service health
docker-compose ps

# Check logs
docker-compose logs backend
```

4. Run migrations:
```bash
docker-compose exec backend alembic upgrade head
```

5. Run E2E tests:
```bash
cd backend
pytest tests/test_e2e.py -v -s
```

6. Stop services:
```bash
docker-compose down
```

### Running All Tests

Run the comprehensive test suite:
```bash
cd /Users/georgistavrev/projs/konfig
bash scripts/run_all_tests.sh
```

This will run:
1. Unit tests with coverage
2. Code quality checks (if ruff is installed)
3. End-to-end tests with Docker

## Test Coverage

The test suite covers:

### Security (test_security.py)
- ✓ Password hashing uniqueness
- ✓ Password verification
- ✓ JWT access token creation/decoding
- ✓ JWT refresh token creation/decoding
- ✓ Invalid token handling
- ✓ Data encryption/decryption
- ✓ Unicode character handling
- ✓ Empty string handling

### Authentication (test_auth.py)
- ✓ Tenant registration
- ✓ Duplicate email prevention
- ✓ Successful login
- ✓ Wrong password handling
- ✓ Non-existent user handling

### Namespaces (test_namespaces.py)
- ✓ Create namespace
- ✓ Authentication requirement
- ✓ Duplicate namespace prevention
- ✓ List namespaces
- ✓ Get specific namespace
- ✓ Non-existent namespace handling
- ✓ Update namespace
- ✓ Delete namespace
- ✓ Multi-tenant isolation

### Configurations (test_configs.py)
- ✓ Create string configuration
- ✓ Create number configuration
- ✓ Create select configuration
- ✓ Create JSON configuration
- ✓ Create secret configuration
- ✓ List configurations
- ✓ Get specific configuration
- ✓ Update configuration
- ✓ Delete configuration
- ✓ Configuration history
- ✓ Encryption at rest
- ✓ Multi-tenant isolation
- ✓ Duplicate key prevention

### End-to-End (test_e2e.py)
- ✓ Health check
- ✓ Complete authentication flow
- ✓ Namespace CRUD operations
- ✓ Configuration CRUD operations
- ✓ All configuration types
- ✓ Version history
- ✓ Secret configurations
- ✓ Multi-tenant isolation with real HTTP requests

## Test Configuration

### pytest.ini
The project includes a pytest configuration file with:
- Test discovery patterns
- Output formatting
- Markers for different test types
- Coverage settings

### conftest.py
Provides shared fixtures:
- `db_session` - Test database session
- `client` - FastAPI test client
- `test_tenant_data` - Sample tenant data
- `test_namespace_data` - Sample namespace data
- `test_config_data` - Sample configuration data

## Continuous Integration

For CI/CD pipelines, use:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd backend
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov
    pytest tests/ --ignore=tests/test_e2e.py --cov=app

- name: Run E2E tests
  run: |
    docker-compose up -d
    docker-compose exec -T backend alembic upgrade head
    cd backend && pytest tests/test_e2e.py -v
    docker-compose down
```

## Troubleshooting

### Tests fail with database connection error
- Ensure PostgreSQL is running (for local tests)
- Check DATABASE_URL in .env file
- For E2E tests, ensure Docker services are healthy

### Import errors
- Install all required dependencies: `pip install -r requirements.txt`
- Ensure you're in the backend directory

### E2E tests timeout
- Increase wait time in test fixtures
- Check Docker container logs: `docker-compose logs backend`
- Ensure ports 8000, 5432, 6379 are not in use

### Authentication errors in tests
- Tests create unique tenant accounts using timestamps
- Each test run should be independent

## Best Practices

1. **Run unit tests frequently** during development
2. **Run integration tests** before committing
3. **Run E2E tests** before pushing to main branch
4. **Check coverage** to ensure new code is tested
5. **Use markers** to run specific test categories:
   ```bash
   pytest -m unit  # Run only unit tests
   pytest -m integration  # Run only integration tests
   pytest -m e2e  # Run only E2E tests
   ```

## Test Metrics

Expected coverage targets:
- Overall: > 80%
- Core modules: > 90%
- Security functions: 100%
- API endpoints: > 85%
