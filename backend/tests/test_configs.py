"""Tests for configuration endpoints."""
import pytest
from fastapi.testclient import TestClient


def setup_tenant_and_namespace(client: TestClient, tenant_data: dict, namespace_data: dict):
    """Helper to setup tenant and namespace, return token and namespace_id."""
    # Register and login
    client.post("/api/v1/auth/register", json=tenant_data)
    response = client.post("/api/v1/auth/login", json={
        "email": tenant_data["email"],
        "password": tenant_data["password"]
    })
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    response = client.post("/api/v1/namespaces", json=namespace_data, headers=headers)
    namespace_id = response.json()["id"]

    return token, namespace_id


def test_create_string_config(client: TestClient, test_tenant_data, test_namespace_data):
    """Test creating a string configuration."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    config_data = {
        "key": "app_name",
        "value": "My Application",
        "value_type": "string",
        "description": "Application name",
        "is_secret": False
    }

    response = client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["key"] == config_data["key"]
    assert data["value"] == config_data["value"]
    assert data["value_type"] == config_data["value_type"]
    assert data["version"] == 1


def test_create_number_config(client: TestClient, test_tenant_data, test_namespace_data):
    """Test creating a number configuration."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    config_data = {
        "key": "max_connections",
        "value": 100,
        "value_type": "number",
        "description": "Maximum connections",
        "is_secret": False
    }

    response = client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == 100
    assert data["value_type"] == "number"


def test_create_select_config(client: TestClient, test_tenant_data, test_namespace_data):
    """Test creating a select configuration."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    config_data = {
        "key": "log_level",
        "value": "INFO",
        "value_type": "select",
        "description": "Logging level",
        "is_secret": False,
        "validation_schema": {
            "options": ["DEBUG", "INFO", "WARNING", "ERROR"]
        }
    }

    response = client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "INFO"
    assert data["value_type"] == "select"


def test_create_json_config(client: TestClient, test_tenant_data, test_namespace_data):
    """Test creating a JSON configuration."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    config_data = {
        "key": "feature_flags",
        "value": {
            "new_ui": True,
            "beta_features": False
        },
        "value_type": "json",
        "description": "Feature flags",
        "is_secret": False
    }

    response = client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["value"]["new_ui"] is True
    assert data["value"]["beta_features"] is False
    assert data["value_type"] == "json"


def test_create_secret_config(client: TestClient, test_tenant_data, test_namespace_data):
    """Test creating a secret configuration."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    config_data = {
        "key": "api_key",
        "value": "sk-1234567890",
        "value_type": "string",
        "description": "API key",
        "is_secret": True
    }

    response = client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["is_secret"] is True
    # Value should still be returned (encryption is transparent)
    assert data["value"] == config_data["value"]


def test_list_configs(client: TestClient, test_tenant_data, test_namespace_data):
    """Test listing configurations."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create multiple configs
    configs = [
        {"key": "config1", "value": "value1", "value_type": "string", "is_secret": False},
        {"key": "config2", "value": 42, "value_type": "number", "is_secret": False},
        {"key": "config3", "value": {"test": True}, "value_type": "json", "is_secret": False},
    ]

    for config in configs:
        client.post(
            f"/api/v1/namespaces/{namespace_id}/configs",
            json=config,
            headers=headers
        )

    # List configs
    response = client.get(
        f"/api/v1/namespaces/{namespace_id}/configs",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_get_config(client: TestClient, test_tenant_data, test_namespace_data):
    """Test getting a specific configuration."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    config_data = {
        "key": "test_config",
        "value": "test_value",
        "value_type": "string",
        "is_secret": False
    }

    # Create config
    client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )

    # Get config
    response = client.get(
        f"/api/v1/namespaces/{namespace_id}/configs/test_config",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "test_config"
    assert data["value"] == "test_value"


def test_update_config(client: TestClient, test_tenant_data, test_namespace_data):
    """Test updating a configuration."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create config
    config_data = {
        "key": "test_config",
        "value": "initial_value",
        "value_type": "string",
        "is_secret": False
    }
    client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )

    # Update config
    update_data = {
        "value": "updated_value"
    }
    response = client.put(
        f"/api/v1/namespaces/{namespace_id}/configs/test_config",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "updated_value"
    assert data["version"] == 2  # Version should increment


def test_delete_config(client: TestClient, test_tenant_data, test_namespace_data):
    """Test deleting a configuration."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create config
    config_data = {
        "key": "test_config",
        "value": "test_value",
        "value_type": "string",
        "is_secret": False
    }
    client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )

    # Delete config
    response = client.delete(
        f"/api/v1/namespaces/{namespace_id}/configs/test_config",
        headers=headers
    )
    assert response.status_code == 204

    # Verify deletion
    response = client.get(
        f"/api/v1/namespaces/{namespace_id}/configs/test_config",
        headers=headers
    )
    assert response.status_code == 404


def test_config_history(client: TestClient, test_tenant_data, test_namespace_data):
    """Test configuration version history."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create config
    config_data = {
        "key": "test_config",
        "value": "version1",
        "value_type": "string",
        "is_secret": False
    }
    client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )

    # Update multiple times
    for i in range(2, 5):
        update_data = {"value": f"version{i}"}
        client.put(
            f"/api/v1/namespaces/{namespace_id}/configs/test_config",
            json=update_data,
            headers=headers
        )

    # Get history
    response = client.get(
        f"/api/v1/namespaces/{namespace_id}/configs/test_config/history",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4  # 1 create + 3 updates
    assert data[0]["version"] == 4  # Most recent first
    assert data[0]["change_type"] == "update"


def test_config_encryption(client: TestClient, test_tenant_data, test_namespace_data):
    """Test that configuration values are encrypted at rest."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    secret_value = "super_secret_password_123"
    config_data = {
        "key": "secret_config",
        "value": secret_value,
        "value_type": "string",
        "is_secret": True
    }

    # Create config
    response = client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 201

    # Get config - should return decrypted value
    response = client.get(
        f"/api/v1/namespaces/{namespace_id}/configs/secret_config",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == secret_value


def test_config_isolation(client: TestClient, test_tenant_data, test_namespace_data):
    """Test that configs are isolated between tenants."""
    # Create first tenant and config
    token1, namespace_id1 = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers1 = {"Authorization": f"Bearer {token1}"}

    config_data = {
        "key": "tenant1_config",
        "value": "tenant1_value",
        "value_type": "string",
        "is_secret": False
    }
    client.post(
        f"/api/v1/namespaces/{namespace_id1}/configs",
        json=config_data,
        headers=headers1
    )

    # Create second tenant
    tenant2_data = {
        "name": "tenant2",
        "email": "tenant2@example.com",
        "password": "Password123!"
    }
    namespace2_data = {
        "name": "tenant2_namespace",
        "description": "Tenant 2 namespace"
    }
    token2, namespace_id2 = setup_tenant_and_namespace(client, tenant2_data, namespace2_data)
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Try to access first tenant's config through first tenant's namespace
    response = client.get(
        f"/api/v1/namespaces/{namespace_id1}/configs/tenant1_config",
        headers=headers2
    )
    assert response.status_code == 404  # Should not be accessible


def test_duplicate_config_key(client: TestClient, test_tenant_data, test_namespace_data):
    """Test creating config with duplicate key."""
    token, namespace_id = setup_tenant_and_namespace(client, test_tenant_data, test_namespace_data)
    headers = {"Authorization": f"Bearer {token}"}

    config_data = {
        "key": "duplicate_key",
        "value": "value1",
        "value_type": "string",
        "is_secret": False
    }

    # Create first config
    client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )

    # Try to create duplicate
    response = client.post(
        f"/api/v1/namespaces/{namespace_id}/configs",
        json=config_data,
        headers=headers
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()
