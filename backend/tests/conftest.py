"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.core.config import settings


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(event_loop) -> Generator[TestClient, None, None]:
    """Get test client."""
    # Create tables synchronously for the test
    async def setup_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    event_loop.run_until_complete(setup_db())

    # Override the get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

    # Cleanup
    async def teardown_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    event_loop.run_until_complete(teardown_db())


@pytest.fixture
def test_user_registration_data():
    """Test user registration data (creates tenant + owner user)."""
    return {
        "tenant_name": "test_company",
        "email": "owner@example.com",
        "password": "TestPassword123!",
        "full_name": "Test Owner"
    }


@pytest.fixture
def test_tenant_data(test_user_registration_data):
    """Alias for test_user_registration_data for backward compatibility."""
    return test_user_registration_data


@pytest.fixture
def test_user_data():
    """Test user data for creating additional users."""
    return {
        "email": "member@example.com",
        "password": "TestPassword123!",
        "full_name": "Test Member",
        "role": "member"
    }


@pytest.fixture
def test_api_key_data():
    """Test API key data."""
    return {
        "name": "test_api_key",
        "scopes": "read,write"
    }


@pytest.fixture
def test_namespace_data():
    """Test namespace data."""
    return {
        "name": "test_namespace",
        "description": "Test namespace for testing"
    }


@pytest.fixture
def test_config_data():
    """Test configuration data."""
    return {
        "key": "test_config",
        "value": "test_value",
        "value_type": "string",
        "description": "Test configuration",
        "is_secret": False
    }


@pytest.fixture
def authenticated_client(client, test_user_registration_data):
    """Get test client with authenticated user (owner role)."""
    # Register and login
    response = client.post("/api/v1/auth/register", json=test_user_registration_data)
    assert response.status_code == 201
    tokens = response.json()

    # Update client headers with auth token
    client.headers.update({"Authorization": f"Bearer {tokens['access_token']}"})

    return client, tokens


@pytest.fixture
def member_user_data():
    """Test data for member user (different from default)."""
    return {
        "email": "member2@example.com",
        "password": "MemberPassword123!",
        "full_name": "Test Member 2",
        "role": "member"
    }


@pytest.fixture
def authenticated_member_client(client, member_user_data):
    """Get test client with authenticated member user."""
    # Register owner first (with different email to avoid conflicts)
    owner_registration = {
        "tenant_name": "member_tenant",
        "email": "member_owner@example.com",
        "password": "OwnerPassword123!",
        "full_name": "Member Tenant Owner"
    }
    response = client.post("/api/v1/auth/register", json=owner_registration)
    assert response.status_code == 201, f"Owner registration failed: {response.json()}"
    owner_tokens = response.json()

    # Create member user
    client.headers.update({"Authorization": f"Bearer {owner_tokens['access_token']}"})
    response = client.post("/api/v1/users", json=member_user_data)
    assert response.status_code == 201, f"Member creation failed: {response.json()}"

    # Login as member
    client.headers.clear()
    login_data = {
        "email": member_user_data["email"],
        "password": member_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Member login failed: {response.json()}"
    member_tokens = response.json()

    # Update client headers with member auth token
    client.headers.update({"Authorization": f"Bearer {member_tokens['access_token']}"})

    return client, member_tokens


@pytest.fixture
def api_key_client(client, test_api_key_data):
    """Get test client with API key authentication."""
    # Register owner first (with different email to avoid conflicts)
    api_key_registration = {
        "tenant_name": "api_key_tenant",
        "email": "api_key_owner@example.com",
        "password": "ApiKeyPassword123!",
        "full_name": "API Key Tenant Owner"
    }
    response = client.post("/api/v1/auth/register", json=api_key_registration)
    assert response.status_code == 201, f"Owner registration failed: {response.json()}"
    tokens = response.json()

    # Create API key
    client.headers.update({"Authorization": f"Bearer {tokens['access_token']}"})
    response = client.post("/api/v1/api-keys", json=test_api_key_data)
    assert response.status_code == 201, f"API key creation failed: {response.json()}"
    api_key_data_response = response.json()

    # Save the actual API key before switching to API key auth
    actual_api_key = api_key_data_response["api_key"]

    # Update client headers with API key
    client.headers.clear()
    client.headers.update({"X-API-Key": actual_api_key})

    # Return client with the full response (including the api_key)
    return client, api_key_data_response
