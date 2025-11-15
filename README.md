# Konfig - Configuration as a Service

A secure, scalable, multi-tenant configuration management platform built with Python FastAPI.

## Features

- **Multi-tenant architecture** with isolated data and strong security boundaries
- **Type-safe configurations** supporting string, number, select, and JSON types
- **Encryption at rest** for all configuration values
- **Version history** and rollback capabilities
- **RESTful API** with OpenAPI documentation
- **JWT-based authentication** with refresh tokens
- **Namespace organization** for logical grouping
- **Docker support** for easy deployment
- **Multiple database support** (PostgreSQL, MySQL, MongoDB, DynamoDB)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if not using Docker)

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd konfig
```

2. Start the services:
```bash
docker-compose up -d
```

3. The API will be available at `http://localhost:8000`
4. API documentation at `http://localhost:8000/docs`

### Local Development

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your configuration

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the development server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
konfig/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py         # Authentication endpoints
│   │   │       ├── namespaces.py   # Namespace management
│   │   │       └── configs.py      # Configuration management
│   │   ├── core/
│   │   │   ├── config.py           # Application settings
│   │   │   └── security.py         # Security utilities
│   │   ├── db/
│   │   │   └── base.py             # Database setup
│   │   ├── models/
│   │   │   ├── tenant.py           # Tenant model
│   │   │   ├── namespace.py        # Namespace model
│   │   │   └── config.py           # Config model
│   │   ├── schemas/
│   │   │   ├── tenant.py           # Tenant schemas
│   │   │   ├── namespace.py        # Namespace schemas
│   │   │   └── config.py           # Config schemas
│   │   └── main.py                 # FastAPI application
│   ├── alembic/                    # Database migrations
│   ├── tests/                      # Test suite
│   ├── Dockerfile
│   └── requirements.txt
├── cli/                            # CLI tool (future)
├── frontend/                       # Web UI (future)
├── deployment/                     # Deployment configs
│   ├── aws/
│   ├── azure/
│   └── heroku/
├── docs/
│   └── SPECIFICATION.md
└── docker-compose.yml
```

## API Usage

### 1. Register a Tenant

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mycompany",
    "email": "admin@mycompany.com",
    "password": "SecurePassword123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@mycompany.com",
    "password": "SecurePassword123"
  }'
```

Save the `access_token` from the response.

### 3. Create a Namespace

```bash
curl -X POST http://localhost:8000/api/v1/namespaces \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "production",
    "description": "Production environment configurations"
  }'
```

### 4. Create a Configuration

```bash
curl -X POST http://localhost:8000/api/v1/namespaces/NAMESPACE_ID/configs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "key": "database_url",
    "value": "postgresql://localhost:5432/mydb",
    "value_type": "string",
    "description": "Database connection URL",
    "is_secret": true
  }'
```

### 5. Get Configuration

```bash
curl -X GET http://localhost:8000/api/v1/namespaces/NAMESPACE_ID/configs/database_url \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Configuration Types

### String
```json
{
  "key": "app_name",
  "value": "My Application",
  "value_type": "string",
  "validation_schema": {
    "min_length": 3,
    "max_length": 50,
    "pattern": "^[a-zA-Z0-9 ]+$"
  }
}
```

### Number
```json
{
  "key": "max_connections",
  "value": 100,
  "value_type": "number",
  "validation_schema": {
    "min_value": 1,
    "max_value": 1000
  }
}
```

### Select
```json
{
  "key": "log_level",
  "value": "INFO",
  "value_type": "select",
  "validation_schema": {
    "options": ["DEBUG", "INFO", "WARNING", "ERROR"]
  }
}
```

### JSON
```json
{
  "key": "feature_flags",
  "value": {
    "new_ui": true,
    "beta_features": false
  },
  "value_type": "json"
}
```

## Security

- All configuration values are encrypted at rest using AES-256
- API communication uses HTTPS/TLS
- JWT tokens for authentication with short expiry times
- Rate limiting to prevent abuse
- Row-level security for multi-tenant data isolation
- Audit logging for all operations

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT signing key
- `ENCRYPTION_KEY` - Data encryption key
- `RATE_LIMIT_PER_MINUTE` - API rate limit

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Deployment

### Docker

```bash
docker-compose up -d
```

### AWS ECS/Fargate

See `deployment/aws/README.md` for detailed instructions.

### Azure App Service

See `deployment/azure/README.md` for detailed instructions.

### Heroku

```bash
heroku create
heroku addons:create heroku-postgresql
heroku addons:create heroku-redis
git push heroku main
```

## Roadmap

- [ ] Client SDKs (Python, JavaScript, Go, Java)
- [ ] CLI tool for configuration management
- [ ] Web UI for easy configuration
- [ ] Webhook notifications
- [ ] Configuration templates
- [ ] A/B testing and feature flags
- [ ] Import/export functionality
- [ ] Advanced analytics
- [ ] Enterprise SSO integration

## Contributing

Contributions are welcome! Please read our contributing guidelines.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: <repository-url>/docs
- Email: support@konfig.io
