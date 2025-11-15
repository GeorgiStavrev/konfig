# Konfig Quick Start Guide

Get up and running with Konfig in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- curl or any HTTP client

## Step 1: Start the Services

```bash
cd konfig
docker-compose up -d
```

Wait a few seconds for the services to start. Check status:

```bash
docker-compose ps
```

You should see:
- `konfig-postgres` (PostgreSQL database)
- `konfig-redis` (Redis cache)
- `konfig-backend` (FastAPI application)

## Step 2: Verify the API is Running

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "app": "Konfig",
  "version": "0.1.0",
  "environment": "development"
}
```

## Step 3: View API Documentation

Open your browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Step 4: Initialize Database

```bash
docker-compose exec backend alembic upgrade head
```

Or if running locally:
```bash
cd backend
alembic upgrade head
```

## Step 5: Run the Example Script

```bash
cd backend
pip install requests  # If not already installed
python scripts/example_usage.py
```

This script will:
1. Register a new tenant
2. Login and get an access token
3. Create a namespace
4. Create various types of configurations
5. List, update, and retrieve configurations
6. Show configuration history

## Step 6: Try It Yourself

### Register a Tenant

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mycompany",
    "email": "you@company.com",
    "password": "YourSecurePassword123!"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@company.com",
    "password": "YourSecurePassword123!"
  }'
```

Save the `access_token` from the response.

### Create a Namespace

```bash
export TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/v1/namespaces \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "development",
    "description": "Development environment"
  }'
```

Save the namespace `id` from the response.

### Create a Configuration

```bash
export NAMESPACE_ID="your_namespace_id_here"

curl -X POST http://localhost:8000/api/v1/namespaces/$NAMESPACE_ID/configs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "key": "api_key",
    "value": "sk-1234567890",
    "value_type": "string",
    "description": "API key for external service",
    "is_secret": true
  }'
```

### Get Configuration

```bash
curl -X GET http://localhost:8000/api/v1/namespaces/$NAMESPACE_ID/configs/api_key \
  -H "Authorization: Bearer $TOKEN"
```

### List All Configurations

```bash
curl -X GET http://localhost:8000/api/v1/namespaces/$NAMESPACE_ID/configs \
  -H "Authorization: Bearer $TOKEN"
```

## Configuration Types Examples

### String Configuration
```json
{
  "key": "app_name",
  "value": "My Application",
  "value_type": "string",
  "description": "Application name"
}
```

### Number Configuration
```json
{
  "key": "timeout",
  "value": 30,
  "value_type": "number",
  "description": "Request timeout in seconds"
}
```

### Select Configuration
```json
{
  "key": "environment",
  "value": "production",
  "value_type": "select",
  "validation_schema": {
    "options": ["development", "staging", "production"]
  }
}
```

### JSON Configuration
```json
{
  "key": "database_config",
  "value": {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "pool_size": 10
  },
  "value_type": "json",
  "description": "Database configuration"
}
```

## Common Operations

### Update a Configuration

```bash
curl -X PUT http://localhost:8000/api/v1/namespaces/$NAMESPACE_ID/configs/api_key \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "value": "sk-9876543210"
  }'
```

### Get Configuration History

```bash
curl -X GET http://localhost:8000/api/v1/namespaces/$NAMESPACE_ID/configs/api_key/history \
  -H "Authorization: Bearer $TOKEN"
```

### Delete a Configuration

```bash
curl -X DELETE http://localhost:8000/api/v1/namespaces/$NAMESPACE_ID/configs/api_key \
  -H "Authorization: Bearer $TOKEN"
```

## View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Database only
docker-compose logs -f postgres
```

## Stop Services

```bash
docker-compose down
```

To remove volumes (database data):
```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If port 8000, 5432, or 6379 is already in use, edit `docker-compose.yml` to change the port mappings.

### Database Connection Error

Ensure PostgreSQL is fully started:
```bash
docker-compose logs postgres
```

### Authentication Error

Make sure you're using the correct access token and it hasn't expired (30 minutes by default).

## Next Steps

1. Read the full [README.md](README.md) for more details
2. Check out the [SPECIFICATION.md](docs/SPECIFICATION.md) for architecture details
3. Explore the API documentation at http://localhost:8000/docs
4. Set up your client application to use Konfig

## Need Help?

- Check the logs: `docker-compose logs`
- Review the API documentation: http://localhost:8000/docs
- Open an issue on GitHub
