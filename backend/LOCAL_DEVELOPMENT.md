# Local Development Guide

This guide shows you how to run the Konfig backend locally with hot reload and debugging support.

## Architecture

- **PostgreSQL**: Runs in Docker on port `5433`
- **Redis**: Runs in Docker on port `6379`
- **Backend**: Runs locally on your host with hot reload on port `8000`

This setup allows you to:
- ✅ Debug with VSCode breakpoints
- ✅ Hot reload on code changes
- ✅ Fast iteration without rebuilding Docker images
- ✅ Use your local IDE and tools

## Quick Start

```bash
# 1. Start PostgreSQL and Redis
make dev-up

# 2. Run database migrations
make db-upgrade

# 3. Start the backend with hot reload
make run
```

The backend is now running at http://localhost:8000 with hot reload enabled!

## VSCode Debugging

### Start Debugging with Hot Reload

1. Press `F5` or go to Run and Debug (⇧⌘D)
2. Select **"FastAPI: Debug Backend"**
3. Set breakpoints anywhere in your code
4. Make a request to trigger the breakpoint

### Debug Configuration Features

The debug configuration includes:
- ✅ **Auto-reload**: Server restarts when you save files
- ✅ **Breakpoints**: Full debugging support
- ✅ **Hot reload**: Changes apply immediately
- ✅ **Environment variables**: Loaded from `.env` automatically

### Available Debug Configurations

- **FastAPI: Debug Backend** - With auto-reload (recommended)
- **FastAPI: Debug Backend (No Reload)** - More stable for complex debugging
- **Python: Debug Current Test File** - Debug tests
- **Python: Debug All Tests** - Debug entire test suite

## Step-by-Step Setup

### 1. Start Services

```bash
# Start PostgreSQL and Redis
make dev-up

# Check they're running
make dev-status

# View logs if needed
make dev-logs
```

Expected output:
```
✓ Services started!
  PostgreSQL: localhost:5433
  Redis: localhost:6379
```

### 2. Run Migrations

```bash
# Apply all migrations
make db-upgrade

# Check current version
make db-current
```

### 3. Run the Backend

Choose one of these options:

#### Option A: Command Line with Hot Reload
```bash
make run
```

#### Option B: VSCode Debug Mode
1. Press `F5`
2. Select "FastAPI: Debug Backend"
3. Server starts with debugging enabled

### 4. Access the Application

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Hot Reload in Action

When you save a file, you'll see:
```
INFO:     Detected file change in 'app/api/v1/users.py'
INFO:     Restarting...
INFO:     Application startup complete
```

The server automatically reloads without losing your place!

## Development Workflow

### Making Changes

1. **Edit code** in `app/` directory
2. **Save file** (⌘S)
3. **Server auto-reloads** (watch terminal)
4. **Test changes** immediately

### Adding a New Model

```bash
# 1. Create/modify model in app/models/
# 2. Create migration
make migration-create MSG='add new model'

# 3. Review migration file in alembic/versions/
# 4. Apply migration
make db-upgrade

# 5. Server auto-reloads with new model
```

### Debugging Issues

```bash
# View database logs
make dev-logs

# Check service status
make dev-status

# Restart services
make dev-down
make dev-up
```

## Common Commands

```bash
# Services
make dev-up              # Start PostgreSQL & Redis
make dev-down            # Stop services
make dev-status          # Check service status
make dev-logs            # View logs

# Backend
make run                 # Run with hot reload

# Database
make db-upgrade          # Run migrations
make db-current          # Show current migration
make migration-create MSG='description'

# Testing
make test                # Run tests
make test-cov            # Tests with coverage

# Code Quality
make format              # Format with black
make lint                # Lint with flake8
```

## Environment Configuration

The backend reads from `.env` file:

```env
# Database connects to Docker PostgreSQL
DATABASE_URL=postgresql://konfig:konfig123@localhost:5433/konfig

# Redis connects to Docker Redis
REDIS_URL=redis://localhost:6379/0

# Debug mode enables hot reload
DEBUG=True
```

## Debugging Tips

### Setting Breakpoints

1. Click left of line number in VSCode
2. Red dot appears
3. Start debug mode (F5)
4. Make request to trigger breakpoint
5. Use debug controls:
   - **F10**: Step over
   - **F11**: Step into
   - **Shift+F11**: Step out
   - **F5**: Continue

### Inspecting Variables

When stopped at a breakpoint:
- **Variables panel**: View all local variables
- **Watch panel**: Add expressions to watch
- **Debug console**: Execute Python code in context
- **Call stack**: See execution path

### Hot Reload Issues

If auto-reload causes problems:
1. Use "FastAPI: Debug Backend (No Reload)" configuration
2. Manually restart when needed (Ctrl+Shift+F5)

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 5433
lsof -i :5433

# Or use different port in .env
DATABASE_URL=postgresql://...@localhost:5434/konfig
```

### Database Connection Failed

```bash
# Verify services are running
make dev-status

# Check logs
make dev-logs

# Restart services
make dev-down && make dev-up
```

### Migrations Out of Sync

```bash
# Check current version
make db-current

# View history
make migration-history

# Upgrade to latest
make db-upgrade
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source ../venv/bin/activate

# Reinstall dependencies
make install
```

### Hot Reload Not Working

1. Check DEBUG=True in `.env`
2. Verify you're using `make run` or debug config with reload
3. Make sure files are saved
4. Check terminal for reload messages

## Performance Tips

### Faster Startup

1. Keep Docker services running (don't stop between sessions)
2. Use SQLite for tests (already configured)
3. Disable unnecessary middleware in development

### Efficient Debugging

1. Use "No Reload" mode for complex debugging sessions
2. Set conditional breakpoints for specific cases
3. Use logging for background tasks
4. Profile slow endpoints with `time` decorators

## Next Steps

- Read [MAKEFILE_GUIDE.md](./MAKEFILE_GUIDE.md) for all available commands
- Check [.vscode/DEBUG_GUIDE.md](./.vscode/DEBUG_GUIDE.md) for VSCode tips
- See [../docker-compose.dev.yml](../docker-compose.dev.yml) for service configuration

## Full Stack Development

To run the entire stack (backend + frontend + services):

```bash
# Stop dev services first
make dev-down

# Run full stack
make docker-up

# View all logs
make docker-logs
```

---

**Happy coding! 🚀**

Your changes are instantly reflected, breakpoints work perfectly, and you have full control over the development environment.
