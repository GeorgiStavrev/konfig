# Quick Start - Local Development

Get up and running in 3 commands! 🚀

## TL;DR

```bash
make dev-up        # Start PostgreSQL & Redis
make db-upgrade    # Run migrations
make run           # Start backend with hot reload
```

**Done!** Backend is running at http://localhost:8000 with hot reload.

## VSCode Debugging

```bash
make dev-up        # Start PostgreSQL & Redis
make db-upgrade    # Run migrations
# Press F5 in VSCode
```

Your breakpoints now work and code reloads on save!

## What's Running?

| Service    | Location          | Purpose                    |
|------------|-------------------|----------------------------|
| PostgreSQL | localhost:5433    | Database (in Docker)       |
| Redis      | localhost:6379    | Cache (in Docker)          |
| Backend    | localhost:8000    | FastAPI (on your host)     |

## Features ✨

- ✅ **Hot Reload**: Save file → Server reloads automatically
- ✅ **VSCode Debug**: Full breakpoint support
- ✅ **Fast**: No Docker rebuild needed for code changes
- ✅ **Database**: PostgreSQL in Docker
- ✅ **Interactive Docs**: http://localhost:8000/docs

## Common Commands

```bash
# Services
make dev-up          # Start database & cache
make dev-down        # Stop services
make dev-status      # Check what's running

# Backend
make run             # Run with hot reload
# Or press F5 in VSCode for debugging

# Database
make db-upgrade      # Apply migrations
make migration-create MSG='add feature'

# Testing
make test            # Run all tests
make test-cov        # With coverage report
```

## First Time Setup

```bash
# 1. Install dependencies (one time)
make install

# 2. Start services
make dev-up

# 3. Run migrations
make db-upgrade

# 4. Start developing!
make run
# OR press F5 in VSCode
```

## Full Guides

- [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) - Complete local dev guide
- [MAKEFILE_GUIDE.md](./MAKEFILE_GUIDE.md) - All make commands
- [.vscode/DEBUG_GUIDE.md](./.vscode/DEBUG_GUIDE.md) - VSCode debugging tips

## Troubleshooting

**Port 8000 already in use?**
```bash
# Stop old backend container
docker stop konfig-backend
```

**Database connection failed?**
```bash
make dev-status     # Check services are running
make dev-logs       # View logs
```

**Need help?**
```bash
make help           # See all commands
```

---

**Happy coding!** Changes reload instantly, debugging just works. 🎉
