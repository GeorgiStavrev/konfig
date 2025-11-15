"""Example script demonstrating Konfig API usage."""
import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000/api/v1"


def print_response(response: requests.Response, title: str):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def main():
    """Run example API calls."""
    print("Konfig API Usage Example")
    print("=" * 60)

    # 1. Register a tenant
    register_data = {
        "name": "example_company",
        "email": "admin@example.com",
        "password": "SecurePassword123!"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response(response, "1. Register Tenant")

    if response.status_code != 201:
        print("\nNote: Tenant might already exist. Proceeding with login...")

    # 2. Login
    login_data = {
        "email": "admin@example.com",
        "password": "SecurePassword123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(response, "2. Login")

    if response.status_code != 200:
        print("\nError: Could not login. Please check credentials.")
        return

    token_data = response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Create a namespace
    namespace_data = {
        "name": "production",
        "description": "Production environment configurations"
    }
    response = requests.post(f"{BASE_URL}/namespaces", json=namespace_data, headers=headers)
    print_response(response, "3. Create Namespace")

    if response.status_code == 201:
        namespace = response.json()
        namespace_id = namespace["id"]
    else:
        # Try to list namespaces and use the first one
        response = requests.get(f"{BASE_URL}/namespaces", headers=headers)
        namespaces = response.json()
        if namespaces:
            namespace_id = namespaces[0]["id"]
            print(f"\nUsing existing namespace: {namespace_id}")
        else:
            print("\nError: Could not create or find namespace.")
            return

    # 4. Create configurations of different types
    configs = [
        {
            "key": "app_name",
            "value": "My Application",
            "value_type": "string",
            "description": "Application name",
            "is_secret": False
        },
        {
            "key": "max_connections",
            "value": 100,
            "value_type": "number",
            "description": "Maximum database connections",
            "is_secret": False
        },
        {
            "key": "log_level",
            "value": "INFO",
            "value_type": "select",
            "description": "Logging level",
            "is_secret": False,
            "validation_schema": {
                "options": ["DEBUG", "INFO", "WARNING", "ERROR"]
            }
        },
        {
            "key": "feature_flags",
            "value": {
                "new_ui": True,
                "beta_features": False,
                "dark_mode": True
            },
            "value_type": "json",
            "description": "Feature flags",
            "is_secret": False
        },
        {
            "key": "database_password",
            "value": "SuperSecretPassword123!",
            "value_type": "string",
            "description": "Database password",
            "is_secret": True
        }
    ]

    for config_data in configs:
        response = requests.post(
            f"{BASE_URL}/namespaces/{namespace_id}/configs",
            json=config_data,
            headers=headers
        )
        print_response(response, f"4. Create Config: {config_data['key']}")

    # 5. List all configurations
    response = requests.get(
        f"{BASE_URL}/namespaces/{namespace_id}/configs",
        headers=headers
    )
    print_response(response, "5. List All Configurations")

    # 6. Get a specific configuration
    response = requests.get(
        f"{BASE_URL}/namespaces/{namespace_id}/configs/app_name",
        headers=headers
    )
    print_response(response, "6. Get Specific Configuration")

    # 7. Update a configuration
    update_data = {
        "value": "My Updated Application"
    }
    response = requests.put(
        f"{BASE_URL}/namespaces/{namespace_id}/configs/app_name",
        json=update_data,
        headers=headers
    )
    print_response(response, "7. Update Configuration")

    # 8. Get configuration history
    response = requests.get(
        f"{BASE_URL}/namespaces/{namespace_id}/configs/app_name/history",
        headers=headers
    )
    print_response(response, "8. Get Configuration History")

    # 9. List namespaces
    response = requests.get(f"{BASE_URL}/namespaces", headers=headers)
    print_response(response, "9. List Namespaces")

    print("\n" + "="*60)
    print("Example completed successfully!")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API.")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\nError: {e}")
