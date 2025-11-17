# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 1. CI Workflow (`ci.yml`)

Runs on every push to `main`/`master` and on all pull requests.

**Jobs:**

#### Lint
- Runs `flake8` for code quality
- Checks formatting with `black`
- Verifies import sorting with `isort`

#### Test
- Runs all tests with `pytest`
- Generates coverage reports
- Uses PostgreSQL and Redis services
- Uploads coverage to Codecov

#### Security
- Scans dependencies with `safety`
- Runs `bandit` for security vulnerabilities
- Uploads security reports as artifacts

#### Type Check
- Runs `mypy` for type checking
- Continues on error (informational only)

### 2. Deploy Workflow (`deploy.yml`)

Runs on pushes to `main`/`master` and version tags.

**Jobs:**

#### Build and Push
- Builds Docker image
- Pushes to Docker Hub (requires secrets)
- Tags images appropriately

#### Deploy Staging
- Deploys to staging environment
- Runs on `main`/`master` branch pushes
- **Note:** Deployment commands need to be customized

#### Deploy Production
- Deploys to production environment
- Runs on version tags (e.g., `v1.0.0`)
- **Note:** Deployment commands need to be customized

## Setup

### Required Secrets

Add these secrets in GitHub repository settings:

1. **DOCKER_USERNAME** - Docker Hub username
2. **DOCKER_PASSWORD** - Docker Hub password/token

### Optional Configuration

#### Codecov
- Sign up at https://codecov.io
- Add your repository
- No additional secrets needed (works with GitHub token)

#### Custom Deployment
Edit `deploy.yml` to add your deployment commands:
- Kubernetes (`kubectl`)
- SSH to servers
- Cloud provider CLIs (AWS, GCP, Azure)

## Local Development

### Pre-commit Hooks

Install pre-commit hooks to run checks before every commit:

```bash
# Install hooks
make pre-commit-install

# Run manually on all files
make pre-commit-run
```

### Run CI Checks Locally

```bash
# Run all CI checks (same as GitHub Actions)
make ci

# Or run individual checks
make lint
make test
make security
```

### Run Github actions locally
```bash
brew install act

# stop any running redis/postgres containers on default ports
act -W .github/workflows/ci.yml --container-architecture linux/amd64
```

## Workflow Triggers

### CI Workflow
```yaml
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
```

### Deploy Workflow
```yaml
on:
  push:
    branches: [ main, master ]  # Staging
    tags: [ 'v*' ]              # Production
```

## Badge Status

Add these badges to your README.md:

```markdown
![CI](https://github.com/YOUR_USERNAME/konfig/workflows/CI/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/konfig/workflows/Deploy/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/konfig/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/konfig)
```

## Customization

### Modify Python Version

Edit the `python-version` in workflow files:

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'  # Change this
```

### Add More Jobs

Add new jobs to `ci.yml`:

```yaml
jobs:
  your-job:
    name: Your Custom Job
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # ... your steps
```

### Environment Variables

Add environment-specific variables:

```yaml
- name: Run tests
  env:
    CUSTOM_VAR: value
  run: pytest
```

## Troubleshooting

### Tests Fail in CI but Pass Locally

1. Check PostgreSQL/Redis service configuration
2. Verify environment variables
3. Check Python version matches
4. Review test logs in GitHub Actions

### Docker Build Fails

1. Verify Dockerfile exists and is valid
2. Check Docker Hub credentials
3. Review build logs

### Deployment Fails

1. Check deployment commands are correct
2. Verify environment secrets
3. Test deployment commands locally

## Best Practices

1. **Always run `make ci` before pushing**
2. **Use pre-commit hooks** to catch issues early
3. **Keep workflows fast** - use caching
4. **Monitor coverage** - aim for >80%
5. **Review security reports** regularly
6. **Tag releases** properly (`v1.0.0`, `v1.0.1`, etc.)

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.io)
- [Docker Hub](https://hub.docker.com)
