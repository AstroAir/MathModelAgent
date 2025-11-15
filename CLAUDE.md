# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MathModelAgent is a mathematical modeling automation system designed specifically for math competitions. It automates the entire process of mathematical modeling, code generation, and paper writing to produce competition-ready submissions.

## Common Commands

### Backend Development
```bash
cd backend
# Install dependencies using uv
uv sync

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
venv\Scripts\activate.bat  # Windows

# Start development server
# macOS/Linux
ENV=DEV uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120 --reload

# Windows
set ENV=DEV && uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120 --reload

# Code quality
ruff check .           # Check for issues
ruff check . --fix     # Auto-fix issues
ruff format .          # Format code
```

### Frontend Development
```bash
cd frontend
# Install dependencies
pnpm i

# Start development server
pnpm run dev

# Build for production
pnpm run build

# TypeScript check
pnpm run build  # Also performs type checking
```

### Docker Deployment
```bash
# Start all services
docker-compose up

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

## Architecture Overview

### Project Structure
- **frontend/**: Vue 3 + TypeScript + Vite web application
- **backend/**: FastAPI-based Python backend with mathematical modeling logic
- **docker-compose.yml**: Container orchestration for development and deployment

### Core Components

#### Backend Architecture

- **FastAPI Application**: Async web framework with WebSocket support
- **Multi-Agent System**:
  - `CoordinatorAgent`: Orchestrates the overall workflow (in `workflow.py`)
  - `ModelerAgent`: Analyzes problems and creates mathematical models
  - `CoderAgent`: Generates and executes Python code using Jupyter notebooks
    - Supports retry logic for error correction
    - Uses local or cloud interpreters (E2B, Daytona)
  - `WriterAgent`: Composes academic papers from modeling results
  - Each agent can use different LLM models configured in `model_config.toml`
- **Code Interpreters**:
  - Local Jupyter-based interpreter (saves notebooks for editing)
  - Cloud interpreters (E2B, Daytona) for remote execution
- **Task Management**: Redis-based queuing and status tracking
- **LLM Integration**: LiteLLM for multi-model support across different agents
- **WebSocket Communication**:
  - Route: `/task/{task_id}`
  - Real-time task progress and result updates
  - Messages defined in `backend/app/schemas/response.py` (`AgentMessage`, `SystemMessage`)
  - Backend publishes to Redis channel `task:{task_id}:messages`
  - Frontend subscribes via WebSocket, parses JSON messages by type

#### Frontend Architecture

- **Vue 3 Composition API** with TypeScript (`<script setup lang="ts">` syntax)
- **Pinia** for state management
- **Tailwind CSS** for styling
- **WebSocket Client**: Real-time task progress updates
- **Multi-page Application**: Chat interface, task details, and configuration
- **API Layer**: Axios wrapper in `frontend/src/utils/request.ts`

### Key Workflow

1. User uploads data files (.txt, .csv, .xlsx, etc.) and provides problem description
2. User selects parameters (template: 国赛/美赛, language, output format: Markdown/LaTeX)
3. System creates modeling task with unique task_id
4. Frontend WebSocket connects to `/task/{task_id}` for real-time updates
5. Agents execute sequentially:
   - Modeler analyzes problem and proposes mathematical approach
   - Coder implements solution in Jupyter notebooks (with error retry logic)
   - Writer generates formatted academic paper
6. Real-time progress updates via WebSocket
7. Results saved to `backend/project/work_dir/{task_id}/`:
   - `notebook.ipynb`: Generated code and execution results
   - `res.md`: Final results in Markdown format
   - Uploaded data files and generated papers

### Configuration Files

- **Backend**:
  - `pyproject.toml`: Python dependencies and ruff configuration
  - `.env.dev`: Environment variables (API keys, Redis URL)
  - `backend/app/config/md_template.toml`: Prompt templates for each agent (customizable)
  - `backend/app/config/model_config.toml`: LLM model configurations per agent
- **Frontend**:
  - `package.json`: Node.js dependencies
  - `.env.development`: Development environment config
- **Docker**: `docker-compose.yml` orchestrates Redis, backend, and frontend services

### Development Environment Requirements

- **Python 3.12+** (managed with uv for package management)
- **Node.js** with pnpm package manager
- **Redis server** (REQUIRED - must be running before backend starts)
- **Docker** (optional, for containerized deployment)

## Important Development Notes

### Backend Development

- **Project Structure**:
  - All new API routes should go in `backend/app/routers/` and be registered in `main.py`
  - Core business logic belongs in `backend/app/core/` (agents, workflow)
  - Utility functions should be placed in `backend/app/utils/`
  - Data models in `backend/app/models/`, schemas in `backend/app/schemas/`
  - Configuration in `backend/app/config/`
- **Coding Patterns**:
  - Use async/await patterns throughout for FastAPI compatibility
  - All API endpoints are asynchronous
  - Data validation via Pydantic models
- **Key Files**:
  - `core/agents.py`: Agent implementations (Modeler, Coder, Writer)
  - `core/workflow.py`: Main modeling workflow orchestration
  - `utils/redis_manager.py`: Redis task and message management
  - `utils/ws_manager.py`: WebSocket connection management
  - `config/setting.py`: Environment variables and global configuration
- **Task & Messaging**:
  - Each modeling task gets a unique `task_id`
  - Task state and messages managed through Redis
  - WebSocket subscribes to `task:{task_id}:messages` channel for real-time updates

### Frontend Development

- **Project Structure**:
  - Page components in `frontend/src/pages/` with `index.vue` as entry point
  - Reusable components in `frontend/src/components/`
  - UI components in `frontend/src/components/ui/` (shadcn-vue based)
  - API calls in `frontend/src/apis/` (organized by business domain)
  - Utilities in `frontend/src/utils/` and `frontend/src/lib/`
- **Coding Patterns**:
  - Use Vue 3 Composition API with `<script setup lang="ts">` syntax
  - Props, emits, and slots should have TypeScript types
  - Complex interactions should be split into smaller components
- **Key Patterns**:
  - API requests go through `src/utils/request.ts` axios instance
  - WebSocket connection for real-time task updates
  - TypeScript path alias `@` points to `src/`

### Customization & Configuration

- **Prompt Templates**: Customize agent prompts in `backend/app/config/md_template.toml`
  - Supports prompt injection for each subtask (modeling, coding, writing)
- **Model Selection**: Configure different LLM models per agent in `model_config.toml`
- **Redis Configuration**: Update `REDIS_URL` in `backend/.env.dev` for local development

### Testing and Quality

- **Backend**:
  - Use ruff for linting and formatting (configured in `pyproject.toml`)
  - Line length: 88 characters
  - Python version: 3.12
- **Frontend**:
  - TypeScript compilation via `pnpm run build`
  - Biome for linting
  - All components should use TypeScript
- **Output Inspection**:
  - Generated files stored in `backend/project/work_dir/{task_id}/`
  - Check `notebook.ipynb` for code execution details
  - Review `res.md` for final results
