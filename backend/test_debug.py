import pytest

def test_debug_registration(client, test_user_registration_data, test_user_data):
    """Debug the registration issue."""
    # Register owner
    response = client.post("/api/v1/auth/register", json=test_user_registration_data)
    print(f"\nRegistration response status: {response.status_code}")
    print(f"Registration response: {response.json()}")
    assert response.status_code == 201
    owner_tokens = response.json()
    
    # Create member user
    client.headers.update({"Authorization": f"Bearer {owner_tokens['access_token']}"})
    print(f"\nCreating user with data: {test_user_data}")
    response = client.post("/api/v1/users", json=test_user_data)
    print(f"Create user response status: {response.status_code}")
    print(f"Create user response: {response.json()}")
    assert response.status_code == 201
