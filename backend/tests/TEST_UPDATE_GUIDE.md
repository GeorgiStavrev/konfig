# Test Update Guide for New Authentication Model

## Overview

The authentication refactoring introduces a new model where:
- **Tenants** are organizations (no user fields)
- **Users** are individuals belonging to tenants (with roles)
- **API Keys** enable service-to-service authentication

This guide explains how to update existing tests to work with the new model.

## New Test Fixtures Available

### In `conftest.py`:

1. **test_user_registration_data** - Data for registering a new tenant with owner user
2. **test_user_data** - Data for creating additional users
3. **test_api_key_data** - Data for creating API keys
4. **authenticated_client** - Client with owner user authentication
5. **authenticated_member_client** - Client with member user authentication
6. **api_key_client** - Client with API key authentication

## Files to Update

### 1. test_auth.py - COMPLETE REWRITE REQUIRED

**Old behavior:**
- Tenants registered/logged in directly with email/password

**New behavior:**
- Registration creates both tenant AND owner user
- Login authenticates users, not tenants
- Returns user info + tenant context in response

**Required changes:**

```python
# OLD (tenant-based auth)
def test_register():
    response = client.post("/api/v1/auth/register", json={
        "name": "Company",
        "email": "user@example.com",
        "password": "pass123"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

# NEW (user-based auth with tenant)
def test_register():
    response = client.post("/api/v1/auth/register", json={
        "tenant_name": "Company",
        "email": "owner@example.com",
        "password": "Password123!",
        "full_name": "Owner Name"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["role"] == "owner"
    assert "tenant_id" in data
    assert "tenant_name" in data
```

**Tests to add:**
- Registration creates tenant + owner user
- Login returns user + tenant info
- Cannot register with duplicate tenant name
- Cannot register with duplicate email
- Login fails with inactive user
- Login fails with inactive tenant
- Token includes user_id in subject

### 2. test_namespaces.py - UPDATE AUTH FIXTURES

**Required changes:**

```python
# OLD
def test_create_namespace(client, test_tenant_data):
    # Register tenant
    response = client.post("/api/v1/auth/register", json=test_tenant_data)
    token = response.json()["access_token"]

    # Create namespace
    client.headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/namespaces", json={...})

# NEW (use fixture)
def test_create_namespace(authenticated_client, test_namespace_data):
    client, tokens = authenticated_client

    # Create namespace (client is already authenticated)
    response = client.post("/api/v1/namespaces", json=test_namespace_data)
    assert response.status_code == 201
```

**Tests to add:**
- Namespaces can be created with JWT token
- Namespaces can be created with API key
- Users can only access namespaces in their tenant
- Members can create namespaces (RBAC test)

### 3. test_configs.py - UPDATE AUTH FIXTURES

**Similar changes to test_namespaces.py:**

```python
# OLD
def test_create_config(client, test_tenant_data):
    # Register + get namespace...

# NEW
def test_create_config(authenticated_client, test_namespace_data, test_config_data):
    client, tokens = authenticated_client

    # Create namespace first
    ns_response = client.post("/api/v1/namespaces", json=test_namespace_data)
    namespace = ns_response.json()

    # Create config
    response = client.post(
        f"/api/v1/namespaces/{namespace['id']}/configs",
        json=test_config_data
    )
    assert response.status_code == 201
```

**Tests to verify:**
- Configs can be created with JWT token
- Configs can be created with API key
- Config history tracking still works
- Encryption/decryption still works

### 4. test_e2e.py - COMPLETE UPDATE REQUIRED

**Old E2E flow:**
1. Register tenant
2. Create namespace
3. Create config
4. Fetch config

**New E2E flow:**
1. Register tenant + owner user
2. Login as owner
3. Create namespace
4. Create config
5. Fetch config with JWT
6. Create API key
7. Fetch config with API key
8. Create additional user (admin)
9. Login as admin
10. Manage resources as admin

**Example new E2E test:**

```python
def test_complete_workflow(client):
    # 1. Register
    registration = {
        "tenant_name": "Test Company",
        "email": "owner@test.com",
        "password": "Password123!",
        "full_name": "Owner User"
    }
    response = client.post("/api/v1/auth/register", json=registration)
    assert response.status_code == 201
    tokens = response.json()

    client.headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 2. Create namespace
    namespace = {"name": "production", "description": "Production configs"}
    response = client.post("/api/v1/namespaces", json=namespace)
    assert response.status_code == 201
    ns_id = response.json()["id"]

    # 3. Create config
    config = {
        "key": "api_url",
        "value": "https://api.example.com",
        "value_type": "string",
        "is_secret": False
    }
    response = client.post(f"/api/v1/namespaces/{ns_id}/configs", json=config)
    assert response.status_code == 201

    # 4. Create API key
    api_key_data = {"name": "production_service", "scopes": "read"}
    response = client.post("/api/v1/api-keys", json=api_key_data)
    assert response.status_code == 201
    api_key = response.json()["api_key"]

    # 5. Fetch config with API key
    client.headers = {"X-API-Key": api_key}
    response = client.get(f"/api/v1/namespaces/{ns_id}/configs/api_url")
    assert response.status_code == 200
    assert response.json()["value"] == "https://api.example.com"
```

### 5. test_security.py - SHOULD STILL PASS

This file tests password hashing and security utilities, which haven't changed.

**Verify:**
- All existing tests still pass
- No changes needed (unless the tests reference tenant models directly)

## New Test Files Created

### test_users.py

Comprehensive tests for user management:
- List users in tenant
- Create users (role-based)
- Get user details
- Update user profiles
- Delete users
- Role-based access control
- Cannot delete self
- Cannot delete last owner

### test_api_keys.py

Comprehensive tests for API key management:
- Create API keys (admin+)
- List API keys
- Revoke API keys
- API key authentication
- API key scopes
- API key expiration
- Last used tracking

## Common Update Patterns

### Pattern 1: Replace tenant registration with user registration

```python
# Before
test_tenant = {"name": "Company", "email": "user@example.com", "password": "pass"}

# After
test_user_registration = {
    "tenant_name": "Company",
    "email": "owner@example.com",
    "password": "Password123!",
    "full_name": "Owner Name"
}
```

### Pattern 2: Use authenticated fixtures

```python
# Before
def test_something(client):
    # Register
    response = client.post("/api/v1/auth/register", json={...})
    token = response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    # ... test code

# After
def test_something(authenticated_client):
    client, tokens = authenticated_client
    # Client is already authenticated - just use it
```

### Pattern 3: Test both auth methods

```python
@pytest.mark.parametrize("auth_client", ["authenticated_client", "api_key_client"])
def test_namespace_with_different_auth(auth_client, test_namespace_data, request):
    """Test namespace creation with both JWT and API key."""
    client, _ = request.getfixturevalue(auth_client)

    response = client.post("/api/v1/namespaces", json=test_namespace_data)
    assert response.status_code == 201
```

## Migration Checklist

- [x] Updated conftest.py with new fixtures
- [x] Created test_users.py (NEW)
- [x] Created test_api_keys.py (NEW)
- [ ] Rewrite test_auth.py
- [ ] Update test_namespaces.py
- [ ] Update test_configs.py
- [ ] Update test_e2e.py
- [ ] Verify test_security.py still passes

## Running Tests

```bash
# Run all tests
make test

# Run specific test file
./venv/bin/pytest backend/tests/test_users.py -v

# Run tests for a specific feature
./venv/bin/pytest backend/tests/ -k "api_key" -v

# Run with coverage
./venv/bin/pytest backend/tests/ --cov=app --cov-report=html
```

## Expected Test Count

After updates, you should have approximately:
- test_auth.py: ~10-15 tests
- test_users.py: ~15-20 tests (NEW)
- test_api_keys.py: ~10-15 tests (NEW)
- test_namespaces.py: ~8-12 tests
- test_configs.py: ~10-15 tests
- test_e2e.py: ~3-5 comprehensive tests
- test_security.py: ~5-8 tests (unchanged)

**Total: ~60-90 tests**

## Troubleshooting

### Issue: "No such column: tenants.email"
- **Cause**: Database still has old schema
- **Fix**: Run `make clean-db && alembic upgrade head`

### Issue: "Authentication failed"
- **Cause**: Using old tenant-based auth endpoints
- **Fix**: Update to new user registration endpoint

### Issue: "User not found"
- **Cause**: Tests trying to access user data but tenant doesn't have users
- **Fix**: Use `test_user_registration_data` fixture instead of `test_tenant_data`

### Issue: "Insufficient permissions"
- **Cause**: Test using member user but endpoint requires admin
- **Fix**: Use `authenticated_client` (owner) instead of `authenticated_member_client`

## Notes

- All tests should use the new fixtures for authentication
- Test both JWT and API key authentication where applicable
- Verify role-based access control (owner/admin/member)
- Check that users are isolated to their tenants
- Ensure API keys work for namespace/config operations
- Verify that user management requires appropriate roles
