# Makefile Guide

This guide explains the available Makefile commands for the Konfig backend.

## Quick Reference

```bash
make help              # Show all available commands
```

## Setup Commands

### Install Dependencies
```bash
make install          # Install production dependencies
make dev              # Install development dependencies (pytest, black, flake8)
```

### Clean Cache Files
```bash
make clean            # Remove __pycache__, *.pyc, .pytest_cache, etc.
```

## Development Commands

### Run the Server
```bash
make run              # Start FastAPI with auto-reload on http://localhost:8000
```

### Run Tests
```bash
make test             # Run all tests with pytest
make test-cov         # Run tests with coverage report (HTML + terminal)
```

### Code Quality
```bash
make lint             # Check code with flake8
make format           # Format code with black
```

## Database Migration Commands

### Create a New Migration
```bash
make migration-create MSG='add user preferences table'
```

This will:
1. Auto-generate a migration based on model changes
2. Create a file in `alembic/versions/`
3. Use the provided message as the migration description

### Amend the Last Migration ⭐

If you made a mistake in the last migration or need to modify it:

```bash
make migration-amend
```

This command will:
1. Find the most recent migration
2. Downgrade the database by one version
3. Delete the migration file
4. Allow you to create a new migration with the correct changes

**Example workflow:**
```bash
# You created a migration but forgot to add a field
make migration-create MSG='add users table'

# Oops! You realize you forgot the 'avatar_url' field
# Add the field to your model, then:
make migration-amend

# Now create the migration again with the complete changes
make migration-create MSG='add users table with avatar'
```

**Important Notes:**
- Only amends the **last** migration (HEAD)
- Downgrades the database first (safe operation)
- The migration file is deleted - make sure you want to do this!
- After amending, you need to create a new migration

### Apply Migrations
```bash
make db-upgrade       # Apply all pending migrations (upgrade to head)
make db-downgrade     # Rollback one migration
```

### View Migration Status
```bash
make db-current       # Show current migration version
make migration-history # Show all migrations (verbose)
```

## Docker Commands

```bash
make docker-up        # Start all docker containers (detached)
make docker-down      # Stop all docker containers
make docker-logs      # View container logs (follow mode)
```

## Common Workflows

### Initial Setup
```bash
make install
make dev
make db-upgrade
make run
```

### Creating a Migration
```bash
# 1. Modify your models in app/models/
# 2. Create migration
make migration-create MSG='add email verification'

# 3. Review the generated migration file in alembic/versions/
# 4. Apply the migration
make db-upgrade

# 5. Verify it worked
make db-current
```

### Fixing a Bad Migration
```bash
# If you just created a migration and it's wrong:
make migration-amend

# Fix your models, then recreate:
make migration-create MSG='corrected migration'
make db-upgrade
```

### Before Committing
```bash
make format           # Format code
make lint             # Check for issues
make test             # Run tests
```

### Running Tests During Development
```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# View HTML coverage report
open htmlcov/index.html
```

## Tips

1. **Always review migrations**: After `make migration-create`, check the generated file in `alembic/versions/` before applying it

2. **Use meaningful messages**: When creating migrations, use descriptive messages that explain what changed

3. **Test migrations**: After creating a migration, test it with `make db-upgrade` in a development environment

4. **Amend carefully**: Only use `make migration-amend` if:
   - The migration hasn't been committed to git yet
   - The migration hasn't been shared with other developers
   - The migration hasn't been applied to production

5. **Check current state**: Before creating migrations, run `make db-current` to see where you are

6. **Clean regularly**: Run `make clean` occasionally to remove cache files

## Troubleshooting

### "No migrations found" when running migration-amend
- You don't have any migrations yet
- Run `make migration-history` to check

### Migration file not found
- The migration might have already been deleted
- Check `alembic/versions/` directory

### Database not in sync
```bash
# Check current version
make db-current

# Check what migrations exist
make migration-history

# Upgrade to latest
make db-upgrade
```

### Flake8 or Black not found
```bash
# Install dev dependencies
make dev
```
