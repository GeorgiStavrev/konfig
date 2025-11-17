"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_register_tenant(client: TestClient, test_tenant_data):
    """Test tenant registration."""
    response = client.post("/api/v1/auth/register", json=test_tenant_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_tenant_data["email"]
    assert data["tenant_name"] == test_tenant_data["tenant_name"]


def test_register_duplicate_email(client: TestClient, test_tenant_data):
    """Test registration with duplicate email."""
    # Register first tenant
    client.post("/api/v1/auth/register", json=test_tenant_data)

    # Try to register with same email
    response = client.post("/api/v1/auth/register", json=test_tenant_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client: TestClient, test_tenant_data):
    """Test successful login."""
    # Register tenant
    client.post("/api/v1/auth/register", json=test_tenant_data)

    # Login
    login_data = {
        "email": test_tenant_data["email"],
        "password": test_tenant_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_tenant_data):
    """Test login with wrong password."""
    # Register tenant
    client.post("/api/v1/auth/register", json=test_tenant_data)

    # Login with wrong password
    login_data = {
        "email": test_tenant_data["email"],
        "password": "WrongPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
