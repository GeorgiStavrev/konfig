"""Tests for namespace endpoints."""
import pytest
from fastapi.testclient import TestClient


def register_and_login(client: TestClient, tenant_data: dict) -> str:
    """Helper to register and return access token."""
    response = client.post("/api/v1/auth/register", json=tenant_data)
    return response.json()["access_token"]


def test_create_namespace(client: TestClient, test_tenant_data, test_namespace_data):
    """Test creating a namespace."""
    token = register_and_login(client, test_tenant_data)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/namespaces", json=test_namespace_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_namespace_data["name"]
    assert data["description"] == test_namespace_data["description"]
    assert "id" in data


def test_create_namespace_without_auth(client: TestClient, test_namespace_data):
    """Test creating namespace without authentication."""
    response = client.post("/api/v1/namespaces", json=test_namespace_data)
    assert response.status_code == 401  # No auth header - unauthorized


def test_create_duplicate_namespace(client: TestClient, test_tenant_data, test_namespace_data):
    """Test creating namespace with duplicate name."""
    token = register_and_login(client, test_tenant_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create first namespace
    client.post("/api/v1/namespaces", json=test_namespace_data, headers=headers)

    # Try to create duplicate
    response = client.post("/api/v1/namespaces", json=test_namespace_data, headers=headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_list_namespaces(client: TestClient, test_tenant_data, test_namespace_data):
    """Test listing namespaces."""
    token = register_and_login(client, test_tenant_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a namespace
    client.post("/api/v1/namespaces", json=test_namespace_data, headers=headers)

    # List namespaces
    response = client.get("/api/v1/namespaces", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == test_namespace_data["name"]


def test_get_namespace(client: TestClient, test_tenant_data, test_namespace_data):
    """Test getting a specific namespace."""
    token = register_and_login(client, test_tenant_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    create_response = client.post("/api/v1/namespaces", json=test_namespace_data, headers=headers)
    namespace_id = create_response.json()["id"]

    # Get namespace
    response = client.get(f"/api/v1/namespaces/{namespace_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == namespace_id
    assert data["name"] == test_namespace_data["name"]


def test_get_nonexistent_namespace(client: TestClient, test_tenant_data):
    """Test getting non-existent namespace."""
    token = register_and_login(client, test_tenant_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Use a random UUID
    response = client.get("/api/v1/namespaces/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


def test_update_namespace(client: TestClient, test_tenant_data, test_namespace_data):
    """Test updating a namespace."""
    token = register_and_login(client, test_tenant_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    create_response = client.post("/api/v1/namespaces", json=test_namespace_data, headers=headers)
    namespace_id = create_response.json()["id"]

    # Update namespace
    update_data = {
        "name": "updated_namespace",
        "description": "Updated description"
    }
    response = client.put(f"/api/v1/namespaces/{namespace_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_delete_namespace(client: TestClient, test_tenant_data, test_namespace_data):
    """Test deleting a namespace."""
    token = register_and_login(client, test_tenant_data)
    headers = {"Authorization": f"Bearer {token}"}

    # Create namespace
    create_response = client.post("/api/v1/namespaces", json=test_namespace_data, headers=headers)
    namespace_id = create_response.json()["id"]

    # Delete namespace
    response = client.delete(f"/api/v1/namespaces/{namespace_id}", headers=headers)
    assert response.status_code == 204

    # Verify deletion
    response = client.get(f"/api/v1/namespaces/{namespace_id}", headers=headers)
    assert response.status_code == 404


def test_namespace_isolation(client: TestClient, test_tenant_data):
    """Test that namespaces are isolated between tenants."""
    # Create first tenant and namespace
    token1 = register_and_login(client, test_tenant_data)
    headers1 = {"Authorization": f"Bearer {token1}"}

    namespace_data = {"name": "tenant1_namespace", "description": "Tenant 1"}
    create_response = client.post("/api/v1/namespaces", json=namespace_data, headers=headers1)
    namespace_id = create_response.json()["id"]

    # Create second tenant
    tenant2_data = {
        "tenant_name": "tenant2",
        "email": "tenant2@example.com",
        "password": "Password123!",
        "full_name": "Tenant 2 Owner"
    }
    token2 = register_and_login(client, tenant2_data)
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Try to access first tenant's namespace
    response = client.get(f"/api/v1/namespaces/{namespace_id}", headers=headers2)
    assert response.status_code == 404  # Should not be accessible
