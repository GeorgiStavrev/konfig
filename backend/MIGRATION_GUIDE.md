# Database Migration Guide

## Overview

This migration implements the new authentication architecture:
- **Tenants**: Organizations/companies (name only, no user fields)
- **Users**: Individuals belonging to tenants (with roles: owner, admin, member)
- **API Keys**: Service-to-service authentication

## Running the Migration

### Option A: Fresh Start (Recommended for Development)

If you're in development and don't have important data:

```bash
# Stop the backend
make docker-down

# Drop the database (if using Docker)
docker volume rm konfig_postgres_data

# Or if using local PostgreSQL
psql -U postgres -c "DROP DATABASE konfig;"
psql -U postgres -c "CREATE DATABASE konfig;"

# Run migrations
cd backend
../venv/bin/alembic upgrade head

# Start the backend
make docker-up
```

### Option B: Migrate Existing Data

If you have existing tenant data to migrate:

1. **Backup your database first!**
   ```bash
   pg_dump -U postgres konfig > backup_$(date +%Y%m%d).sql
   ```

2. **Create a data migration script** (example):
   ```python
   # migration_script.py
   # This would migrate existing tenant users to the new User model
   from app.db.base import SessionLocal
   from app.models import Tenant, User, UserRole

   async def migrate_tenants_to_users():
       async with SessionLocal() as db:
           # Get all existing tenants
           tenants = await db.execute(select(Tenant))

           for tenant in tenants:
               # If old tenant had email/password, create owner user
               if hasattr(tenant, 'email'):
                   user = User(
                       tenant_id=tenant.id,
                       email=tenant.email,
                       hashed_password=tenant.hashed_password,
                       role=UserRole.OWNER
                   )
                   db.add(user)

           await db.commit()
   ```

3. **Run the migration**:
   ```bash
   cd backend
   ../venv/bin/alembic upgrade head
   python migration_script.py
   ```

## Verification

After migration, verify the schema:

```sql
-- Check tables exist
\dt

-- Should show:
-- tenants
-- users
-- api_keys
-- namespaces
-- configs
-- config_history

-- Verify tenant structure
\d tenants
-- Should NOT have: email, hashed_password, api_key_hash

-- Verify users table
\d users
-- Should have: tenant_id, email, hashed_password, role

-- Verify api_keys table
\d api_keys
-- Should have: tenant_id, key_hash, prefix, scopes
```

## Post-Migration Steps

1. **Create first tenant and owner user**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "tenant_name": "My Company",
       "email": "admin@example.com",
       "password": "secure_password",
       "full_name": "Admin User"
     }'
   ```

2. **Create API key** (using the access token from step 1):
   ```bash
   curl -X POST http://localhost:8000/api/v1/api-keys \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Production Service",
       "scopes": "read,write"
     }'
   ```

## Rollback

If you need to rollback the migration:

```bash
cd backend
../venv/bin/alembic downgrade base
```

**Warning**: This will drop all tables!

## Common Issues

### Issue: "relation already exists"
- Solution: You already have tables. Either drop them or use Option A (fresh start)

### Issue: "module 'app.models' has no attribute 'User'"
- Solution: Make sure you've pulled all the new model files

### Issue: psycopg2 build errors
- Solution: If using Python 3.13, you may need to downgrade to Python 3.11 or 3.12
  ```bash
  pyenv install 3.11
  pyenv local 3.11
  python -m venv venv
  ```

## New Authentication Flow

### For Web/Mobile (Users):
1. Register: `POST /api/v1/auth/register` → Creates tenant + owner user
2. Login: `POST /api/v1/auth/login` → Returns JWT tokens
3. Use: Include `Authorization: Bearer <token>` header

### For Services (API Keys):
1. Admin creates key: `POST /api/v1/api-keys`
2. Service uses: Include `X-API-Key: konfig_<key>` header

Both authentication methods work for namespace and config endpoints!
