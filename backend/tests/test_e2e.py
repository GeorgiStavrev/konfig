"""End-to-end tests for the Konfig application.

These tests are meant to be run against a live instance of the application.
Run with: pytest tests/test_e2e.py -v
"""
import pytest
import requests
import time
from typing import Dict, Tuple


# Base URL for the API
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


@pytest.fixture(scope="module")
def wait_for_api():
    """Wait for the API to be ready."""
    max_retries = 30
    retry_delay = 1

    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"\nAPI is ready after {i+1} attempts")
                return True
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                print(f"\nWaiting for API... attempt {i+1}/{max_retries}")
                time.sleep(retry_delay)
            else:
                pytest.skip("API is not available")

    pytest.skip("API did not become ready in time")


@pytest.fixture(scope="module")
def test_tenant(wait_for_api) -> Tuple[Dict, str]:
    """Create a test tenant and return tenant data and access token."""
    tenant_data = {
        "name": f"e2e_test_company_{int(time.time())}",
        "email": f"e2e_test_{int(time.time())}@example.com",
        "password": "E2ETestPassword123!"
    }

    # Register
    response = requests.post(f"{API_BASE}/auth/register", json=tenant_data)
    assert response.status_code == 201, f"Registration failed: {response.text}"

    # Login
    login_data = {
        "email": tenant_data["email"],
        "password": tenant_data["password"]
    }
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"

    token = response.json()["access_token"]
    return tenant_data, token


def test_e2e_health_check(wait_for_api):
    """Test the health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


def test_e2e_authentication_flow(wait_for_api):
    """Test complete authentication flow."""
    # Register
    tenant_data = {
        "name": f"auth_test_{int(time.time())}",
        "email": f"auth_test_{int(time.time())}@example.com",
        "password": "TestPassword123!"
    }

    response = requests.post(f"{API_BASE}/auth/register", json=tenant_data)
    assert response.status_code == 201
    registered_tenant = response.json()
    assert "id" in registered_tenant
    assert registered_tenant["email"] == tenant_data["email"]

    # Login
    login_data = {
        "email": tenant_data["email"],
        "password": tenant_data["password"]
    }
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Try wrong password
    wrong_login = {
        "email": tenant_data["email"],
        "password": "WrongPassword"
    }
    response = requests.post(f"{API_BASE}/auth/login", json=wrong_login)
    assert response.status_code == 401


def test_e2e_namespace_crud(test_tenant):
    """Test complete namespace CRUD operations."""
    tenant_data, token = test_tenant
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    namespace_data = {
        "name": f"e2e_namespace_{int(time.time())}",
        "description": "E2E test namespace"
    }
    response = requests.post(f"{API_BASE}/namespaces", json=namespace_data, headers=headers)
    assert response.status_code == 201
    namespace = response.json()
    namespace_id = namespace["id"]
    assert namespace["name"] == namespace_data["name"]

    # List namespaces
    response = requests.get(f"{API_BASE}/namespaces", headers=headers)
    assert response.status_code == 200
    namespaces = response.json()
    assert len(namespaces) >= 1
    assert any(ns["id"] == namespace_id for ns in namespaces)

    # Get namespace
    response = requests.get(f"{API_BASE}/namespaces/{namespace_id}", headers=headers)
    assert response.status_code == 200
    fetched_namespace = response.json()
    assert fetched_namespace["id"] == namespace_id

    # Update namespace
    update_data = {
        "description": "Updated description"
    }
    response = requests.put(f"{API_BASE}/namespaces/{namespace_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_namespace = response.json()
    assert updated_namespace["description"] == update_data["description"]

    # Delete namespace
    response = requests.delete(f"{API_BASE}/namespaces/{namespace_id}", headers=headers)
    assert response.status_code == 204

    # Verify deletion
    response = requests.get(f"{API_BASE}/namespaces/{namespace_id}", headers=headers)
    assert response.status_code == 404


def test_e2e_config_crud(test_tenant):
    """Test complete configuration CRUD operations."""
    tenant_data, token = test_tenant
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    namespace_data = {
        "name": f"config_test_ns_{int(time.time())}",
        "description": "Config test namespace"
    }
    response = requests.post(f"{API_BASE}/namespaces", json=namespace_data, headers=headers)
    namespace_id = response.json()["id"]

    # Create string config
    config_data = {
        "key": "app_name",
        "value": "My Application",
        "value_type": "string",
        "description": "Application name",
        "is_secret": False
    }
    response = requests.post(
        f"{API_BASE}/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 201
    config = response.json()
    assert config["key"] == config_data["key"]
    assert config["value"] == config_data["value"]
    assert config["version"] == 1

    # List configs
    response = requests.get(
        f"{API_BASE}/namespaces/{namespace_id}/configs",
        headers=headers
    )
    assert response.status_code == 200
    configs = response.json()
    assert len(configs) >= 1

    # Get config
    response = requests.get(
        f"{API_BASE}/namespaces/{namespace_id}/configs/app_name",
        headers=headers
    )
    assert response.status_code == 200
    fetched_config = response.json()
    assert fetched_config["key"] == "app_name"

    # Update config
    update_data = {
        "value": "Updated Application Name"
    }
    response = requests.put(
        f"{API_BASE}/namespaces/{namespace_id}/configs/app_name",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    updated_config = response.json()
    assert updated_config["value"] == update_data["value"]
    assert updated_config["version"] == 2

    # Delete config
    response = requests.delete(
        f"{API_BASE}/namespaces/{namespace_id}/configs/app_name",
        headers=headers
    )
    assert response.status_code == 204


def test_e2e_config_types(test_tenant):
    """Test all configuration types."""
    tenant_data, token = test_tenant
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    namespace_data = {
        "name": f"types_test_ns_{int(time.time())}",
        "description": "Config types test"
    }
    response = requests.post(f"{API_BASE}/namespaces", json=namespace_data, headers=headers)
    namespace_id = response.json()["id"]

    # Test string type
    string_config = {
        "key": "string_config",
        "value": "test string",
        "value_type": "string",
        "is_secret": False
    }
    response = requests.post(
        f"{API_BASE}/namespaces/{namespace_id}/configs",
        json=string_config,
        headers=headers
    )
    assert response.status_code == 201

    # Test number type
    number_config = {
        "key": "number_config",
        "value": 42,
        "value_type": "number",
        "is_secret": False
    }
    response = requests.post(
        f"{API_BASE}/namespaces/{namespace_id}/configs",
        json=number_config,
        headers=headers
    )
    assert response.status_code == 201

    # Test select type
    select_config = {
        "key": "select_config",
        "value": "option1",
        "value_type": "select",
        "validation_schema": {
            "options": ["option1", "option2", "option3"]
        },
        "is_secret": False
    }
    response = requests.post(
        f"{API_BASE}/namespaces/{namespace_id}/configs",
        json=select_config,
        headers=headers
    )
    assert response.status_code == 201

    # Test JSON type
    json_config = {
        "key": "json_config",
        "value": {
            "nested": {
                "key": "value"
            },
            "array": [1, 2, 3],
            "boolean": True
        },
        "value_type": "json",
        "is_secret": False
    }
    response = requests.post(
        f"{API_BASE}/namespaces/{namespace_id}/configs",
        json=json_config,
        headers=headers
    )
    assert response.status_code == 201
    created_json = response.json()
    assert created_json["value"]["nested"]["key"] == "value"
    assert created_json["value"]["array"] == [1, 2, 3]


def test_e2e_config_history(test_tenant):
    """Test configuration version history."""
    tenant_data, token = test_tenant
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    namespace_data = {
        "name": f"history_test_ns_{int(time.time())}",
        "description": "History test"
    }
    response = requests.post(f"{API_BASE}/namespaces", json=namespace_data, headers=headers)
    namespace_id = response.json()["id"]

    # Create config
    config_data = {
        "key": "versioned_config",
        "value": "version 1",
        "value_type": "string",
        "is_secret": False
    }
    response = requests.post(
        f"{API_BASE}/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 201

    # Update config multiple times
    for i in range(2, 6):
        update_data = {"value": f"version {i}"}
        response = requests.put(
            f"{API_BASE}/namespaces/{namespace_id}/configs/versioned_config",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200

    # Get history
    response = requests.get(
        f"{API_BASE}/namespaces/{namespace_id}/configs/versioned_config/history",
        headers=headers
    )
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 5  # 1 create + 4 updates
    assert history[0]["version"] == 5  # Most recent first
    assert history[-1]["version"] == 1  # Oldest last


def test_e2e_secret_configs(test_tenant):
    """Test secret configuration handling."""
    tenant_data, token = test_tenant
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    namespace_data = {
        "name": f"secret_test_ns_{int(time.time())}",
        "description": "Secret test"
    }
    response = requests.post(f"{API_BASE}/namespaces", json=namespace_data, headers=headers)
    namespace_id = response.json()["id"]

    # Create secret config
    secret_data = {
        "key": "database_password",
        "value": "SuperSecretPassword123!",
        "value_type": "string",
        "is_secret": True
    }
    response = requests.post(
        f"{API_BASE}/namespaces/{namespace_id}/configs",
        json=secret_data,
        headers=headers
    )
    assert response.status_code == 201
    created_secret = response.json()
    assert created_secret["is_secret"] is True

    # Retrieve secret - should still return the value (encryption is transparent)
    response = requests.get(
        f"{API_BASE}/namespaces/{namespace_id}/configs/database_password",
        headers=headers
    )
    assert response.status_code == 200
    fetched_secret = response.json()
    assert fetched_secret["value"] == secret_data["value"]
    assert fetched_secret["is_secret"] is True


def test_e2e_multi_tenant_isolation(wait_for_api):
    """Test that data is properly isolated between tenants."""
    # Create first tenant
    tenant1_data = {
        "name": f"tenant1_{int(time.time())}",
        "email": f"tenant1_{int(time.time())}@example.com",
        "password": "Password123!"
    }
    response = requests.post(f"{API_BASE}/auth/register", json=tenant1_data)
    assert response.status_code == 201

    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": tenant1_data["email"],
        "password": tenant1_data["password"]
    })
    token1 = response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Create namespace for tenant 1
    namespace_data = {
        "name": f"tenant1_ns_{int(time.time())}",
        "description": "Tenant 1 namespace"
    }
    response = requests.post(f"{API_BASE}/namespaces", json=namespace_data, headers=headers1)
    namespace1_id = response.json()["id"]

    # Create config for tenant 1
    config_data = {
        "key": "tenant1_secret",
        "value": "tenant1_secret_value",
        "value_type": "string",
        "is_secret": True
    }
    requests.post(
        f"{API_BASE}/namespaces/{namespace1_id}/configs",
        json=config_data,
        headers=headers1
    )

    # Create second tenant
    tenant2_data = {
        "name": f"tenant2_{int(time.time())}",
        "email": f"tenant2_{int(time.time())}@example.com",
        "password": "Password123!"
    }
    response = requests.post(f"{API_BASE}/auth/register", json=tenant2_data)
    assert response.status_code == 201

    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": tenant2_data["email"],
        "password": tenant2_data["password"]
    })
    token2 = response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Try to access tenant1's namespace with tenant2's token
    response = requests.get(f"{API_BASE}/namespaces/{namespace1_id}", headers=headers2)
    assert response.status_code == 404

    # Try to access tenant1's config with tenant2's token
    response = requests.get(
        f"{API_BASE}/namespaces/{namespace1_id}/configs/tenant1_secret",
        headers=headers2
    )
    assert response.status_code == 404

    # Verify tenant1 can still access their own data
    response = requests.get(f"{API_BASE}/namespaces/{namespace1_id}", headers=headers1)
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
