# Contributing to MathModelAgent

First off, thank you for considering contributing to MathModelAgent! 🎉

This document provides guidelines for contributing to the project. Following these guidelines helps maintain code quality and makes the contribution process smooth for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## 📜 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, Node.js version)
- Relevant logs or screenshots

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml) when creating issues.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the proposed feature
- Explain why this enhancement would be useful
- Include examples of how it would be used

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml).

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:

- `good first issue` - Simple issues for newcomers
- `help wanted` - Issues where we need community help
- `documentation` - Documentation improvements

### Pull Requests

1. Fork the repository
2. Create a new branch from `develop` (not `main`)
3. Make your changes
4. Test your changes thoroughly
5. Submit a pull request

## 🛠️ Development Setup

### Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **Redis**
- **pnpm** (for frontend)
- **uv** (for backend, optional but recommended)

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/jihe520/MathModelAgent.git
cd MathModelAgent
```

2. **Use the startup script**

```bash
# Windows
.\start.bat

# Linux/macOS
chmod +x start.sh
./start.sh

# Or with Docker
docker-compose up
```

3. **Manual setup** (if you prefer)

**Backend:**

```bash
cd backend
pip install uv
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat
ENV=DEV uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**

```bash
cd frontend
pnpm install
pnpm run dev
```

## 📁 Project Structure

```
MathModelAgent/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── config/      # Configuration files
│   │   ├── core/        # Core functionality
│   │   ├── agents/      # Multi-agent system
│   │   ├── api/         # API endpoints
│   │   └── main.py      # Application entry point
│   ├── project/         # Generated project files
│   └── pyproject.toml   # Python dependencies
├── frontend/            # Vue.js frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── pages/       # Page components
│   │   ├── stores/      # Pinia stores
│   │   └── apis/        # API client
│   └── package.json     # Node dependencies
├── docs/                # Documentation
├── .github/             # GitHub templates and workflows
└── docker-compose.yml   # Docker configuration
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## 💻 Coding Standards

### Python (Backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints where applicable
- Format code with **Ruff**: `uv run ruff format .`
- Lint code with **Ruff**: `uv run ruff check .`
- Maximum line length: 88 characters
- Add docstrings to all public functions and classes

**Example:**

```python
from typing import Optional

def process_model_output(
    output: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> dict:
    """
    Process the output from the language model.

    Args:
        output: Raw output from the model
        temperature: Sampling temperature
        max_tokens: Maximum number of tokens to generate

    Returns:
        Processed output as a dictionary
    """
    # Implementation here
    pass
```

### TypeScript/Vue (Frontend)

- Follow Vue 3 Composition API best practices
- Use TypeScript for type safety
- Format code with **Biome**: `pnpm exec biome format --write .`
- Lint code with **Biome**: `pnpm exec biome check .`
- Use `<script setup>` syntax for components
- Keep components focused and reusable

**Example:**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  initialCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  initialCount: 0
})

const count = ref(props.initialCount)
const doubleCount = computed(() => count.value * 2)

function increment() {
  count.value++
}
</script>

<template>
  <div>
    <h2>{{ title }}</h2>
    <p>Count: {{ count }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>
```

### General Guidelines

- Write clear, self-documenting code
- Add comments for complex logic
- Keep functions small and focused
- Avoid code duplication
- Write unit tests for new features
- Update documentation when changing functionality

## 📝 Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**

```
feat(agents): add multi-agent collaboration feature

Implemented a new system for agents to collaborate on complex tasks.
This includes task distribution and result aggregation.

Closes #123
```

```
fix(backend): resolve Redis connection timeout issue

Fixed a bug where Redis connections would timeout after 30 seconds
of inactivity by implementing connection pooling.

Fixes #456
```

## 🔄 Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**

   - Write code following the coding standards
   - Add/update tests as needed
   - Update documentation

3. **Test your changes**

   - Run the linters
   - Run existing tests
   - Test manually in the browser/terminal

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**

   - Use the [PR template](.github/pull_request_template.md)
   - Link related issues
   - Provide a clear description of changes
   - Add screenshots for UI changes
   - Request review from maintainers

7. **Address review feedback**

   - Make requested changes
   - Push updates to the same branch
   - Respond to comments

8. **Merge**
   - Once approved, a maintainer will merge your PR
   - Your contribution will be credited in the release notes

## 🎯 Development Workflow

### Backend Development

```bash
# Install dependencies
cd backend
uv sync

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate.bat

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run development server
ENV=DEV uvicorn app.main:app --reload
```

### Frontend Development

```bash
# Install dependencies
cd frontend
pnpm install

# Run linter
pnpm exec biome check .

# Run formatter
pnpm exec biome format --write .

# Run development server
pnpm run dev

# Build for production
pnpm run build
```

### Testing

```bash
# Backend tests (when available)
cd backend
uv run pytest

# Frontend tests (when available)
cd frontend
pnpm test
```

## 🐛 Debugging

### Backend Debugging

- Check logs in the terminal where the backend is running
- Use `icecream` for debugging: `from icecream import ic; ic(variable)`
- Check Redis connection: `redis-cli ping`

### Frontend Debugging

- Open browser DevTools (F12)
- Check the Console tab for errors
- Use Vue DevTools extension
- Check Network tab for API calls

## 📚 Resources

- [Project Documentation](./docs/)
- [Architecture Documentation](./ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [DeepWiki](https://deepwiki.com/jihe520/MathModelAgent)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [LiteLLM Documentation](https://docs.litellm.ai/)

## 💬 Community

- **QQ Group**: [699970403](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=rFKquDTSxKcWpEhRgpJD-dPhTtqLwJ9r&authKey=xYKvCFG5My4uYZTbIIoV5MIPQedW7hYzf0%2Fbs4EUZ100UegQWcQ8xEEgTczHsyU6&noverify=0&group_code=699970403)
- **Discord**: [Join our Discord](https://discord.gg/3Jmpqg5J)
- **GitHub Issues**: [Report issues](https://github.com/jihe520/MathModelAgent/issues)

## 🙏 Thank You

Your contributions make MathModelAgent better for everyone. Thank you for being part of our community!

---

**Questions?** Feel free to ask in our community channels or create a [question issue](.github/ISSUE_TEMPLATE/question.yml).
