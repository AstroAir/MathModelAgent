# Pre-commit Hooks Setup Guide

This document provides comprehensive instructions for setting up and using pre-commit hooks in the MathModelAgent project to ensure consistent code quality and style across the entire codebase.

## Overview

Pre-commit hooks automatically run code quality checks before each commit, preventing non-compliant code from entering the repository. Our configuration includes:

### Backend (Python) Checks
- **Ruff**: Code formatting, import sorting, and linting (replaces Black, isort, and flake8)
- **Bandit**: Security vulnerability scanning
- **MyPy**: Static type checking
- **Pydocstyle**: Docstring validation

### Frontend (JavaScript/TypeScript) Checks
- **Biome**: Code formatting and linting (replaces Prettier and ESLint)
- **Vue-tsc**: TypeScript type checking for Vue components

### General Checks
- Trailing whitespace removal
- End-of-file newline enforcement
- Large file detection (>1MB)
- Merge conflict marker detection
- YAML/JSON/TOML syntax validation
- Docker file linting with Hadolint
- Markdown linting
- Shell script linting with ShellCheck
- Conventional commit message validation

## Installation

### Prerequisites

Ensure you have the following installed:
- Python 3.12+ with uv package manager
- Node.js 18+ with pnpm package manager
- Git

### Step 1: Install Pre-commit

```bash
# Install pre-commit globally
pip install pre-commit

# Or using uv (recommended for this project)
uv tool install pre-commit
```

### Step 2: Install Pre-commit Hooks

From the project root directory:

```bash
# Install the git hook scripts
pre-commit install

# Install commit-msg hook for conventional commits
pre-commit install --hook-type commit-msg

# Install pre-push hook (optional)
pre-commit install --hook-type pre-push
```

### Step 3: Install Project Dependencies

```bash
# Backend dependencies
cd backend
uv sync --dev
cd ..

# Frontend dependencies
cd frontend
pnpm install
cd ..
```

## Usage

### Automatic Execution

Once installed, pre-commit hooks will run automatically on every `git commit`. If any hook fails, the commit will be blocked until issues are resolved.

### Manual Execution

Run hooks manually on all files:
```bash
pre-commit run --all-files
```

Run hooks on specific files:
```bash
pre-commit run --files backend/app/main.py frontend/src/App.vue
```

Run a specific hook:
```bash
pre-commit run ruff --all-files
pre-commit run biome-check --all-files
```

### Bypassing Hooks (Not Recommended)

In exceptional cases, you can bypass hooks:
```bash
git commit --no-verify -m "Emergency fix"
```

## Configuration Files

The pre-commit setup includes several configuration files:

- `.pre-commit-config.yaml`: Main pre-commit configuration
- `.bandit`: Bandit security scanner configuration
- `.yamllint.yml`: YAML linting rules
- `mypy.ini`: MyPy type checking configuration
- `backend/pyproject.toml`: Ruff configuration (existing)
- `frontend/biome.json`: Biome configuration (existing)

## Troubleshooting

### Common Issues

1. **Hook installation fails**
   ```bash
   # Clear pre-commit cache and reinstall
   pre-commit clean
   pre-commit install --install-hooks
   ```

2. **MyPy import errors**
   ```bash
   # Install missing type stubs
   cd backend
   uv add --dev types-requests types-redis
   ```

3. **Biome not found**
   ```bash
   # Ensure frontend dependencies are installed
   cd frontend
   pnpm install
   ```

4. **Permission errors on Windows**
   ```bash
   # Run as administrator or use WSL
   ```

### Updating Hooks

Update to latest hook versions:
```bash
pre-commit autoupdate
```

## Development Workflow

### Recommended Workflow

1. Make your changes
2. Run tests locally
3. Commit changes (hooks run automatically)
4. Fix any issues reported by hooks
5. Commit again if fixes were needed
6. Push to repository

### IDE Integration

Configure your IDE to run the same tools:

**VS Code**: Install extensions for Ruff, Biome, and MyPy
**PyCharm**: Configure Ruff as external tool and enable MyPy plugin

## Hook Details

### Python Hooks (Backend)

- **ruff**: Fast Python linter and formatter
- **bandit**: Security vulnerability scanner
- **mypy**: Static type checker
- **pydocstyle**: Docstring style checker

### JavaScript/TypeScript Hooks (Frontend)

- **biome-check**: Fast formatter and linter
- **vue-tsc**: TypeScript compiler for Vue

### General Hooks

- **trailing-whitespace**: Removes trailing spaces
- **end-of-file-fixer**: Ensures files end with newline
- **check-yaml/json/toml**: Syntax validation
- **check-merge-conflict**: Detects merge markers
- **check-added-large-files**: Prevents large file commits
- **hadolint-docker**: Docker file best practices
- **markdownlint**: Markdown formatting
- **shellcheck**: Shell script analysis

## Customization

### Disabling Specific Hooks

Edit `.pre-commit-config.yaml` to exclude hooks:
```yaml
exclude: ^(path/to/exclude|another/path)$
```

### Adding New Hooks

Add new repositories and hooks to `.pre-commit-config.yaml`:
```yaml
- repo: https://github.com/new-repo/hook
  rev: v1.0.0
  hooks:
    - id: new-hook
```

## CI Integration

The configuration includes CI settings for pre-commit.ci service:
- Automatic fixes on pull requests
- Weekly dependency updates
- Consistent formatting across contributors

## Support

For issues or questions:
1. Check this documentation
2. Review hook-specific documentation
3. Check project issues on GitHub
4. Contact the development team
