# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MathModelAgent is a mathematical modeling automation system designed specifically for math competitions. It automates the entire process of mathematical modeling, code generation, and paper writing to produce competition-ready submissions.

**Key Features**:
- Multi-agent system (Coordinator, Modeler, Coder, Writer)
- Local and cloud code interpreters (Jupyter, E2B)
- Real-time WebSocket communication
- Support for multiple LLM providers via LiteLLM
- Automatic language detection (Chinese/English)
- File upload and compression support
- Literature search integration (OpenAlex)
- Web search capabilities (Tavily, Exa)


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


## API Routes Reference

### Modeling Routes (`modeling_router.py`)
- `POST /modeling` - Submit custom modeling task with file uploads
- `POST /example` - Run built-in example task
- `POST /validate-api-key` - Validate LLM API key
- `POST /validate-openalex-email` - Validate OpenAlex email
- `POST /save-api-config` - Save API configuration

### File Management Routes (`files_router.py`)
- `GET /{task_id}/files` - Get all files for a task
- `GET /{task_id}/download-url` - Get download URL for a file
- `GET /{task_id}/download-all` - Download all files as ZIP
- `GET /{task_id}/file-content` - Get specific file content
- `POST /{task_id}/upload` - Upload files to task directory
- `DELETE /{task_id}/file` - Delete a file

### History Routes (`history_router.py`)
- `GET /history/tasks` - Get task history list
- `GET /history/tasks/{task_id}` - Get specific task details
- `PUT /history/tasks/{task_id}` - Update task information
- `DELETE /history/tasks/{task_id}` - Delete task
- `POST /history/tasks/{task_id}/pin` - Pin/unpin task

### Common Routes (`common_router.py`)
- `GET /` - Health check
- `GET /config` - Get system configuration
- `GET /writer_seque` - Get paper section sequence
- `GET /track` - Get task token usage and cost
- `GET /status` - Get service status (backend, Redis)

### Settings Routes (`settings_router.py`)
- `GET /api/settings/profile` - Get user profile
- `PUT /api/settings/profile` - Update user profile
- `GET /api/settings/preferences` - Get user preferences
- `PUT /api/settings/preferences` - Update preferences
- `GET /api/settings/security/sessions` - Get active sessions

### Prompt Routes (`prompt_router.py`)
- `POST /api/prompt/optimize` - Optimize user prompt using LLM

### Search Routes (`search_router.py`)
- `POST /search/web` - Perform web search
- `POST /search/content` - Get content for URLs (Exa only)
- `POST /search/similar` - Find similar pages (Exa only)

### WebSocket Routes (`ws_router.py`)
- `WS /task/{task_id}` - Real-time task updates via WebSocket

### Static Files
- `GET /static/{task_id}/{filename}` - Access generated files



## Configuration Files

### Backend Configuration

#### Environment Variables (`.env.dev`)
```bash
# Agent Configuration
COORDINATOR_API_KEY=sk-xxx
COORDINATOR_MODEL=gpt-4
COORDINATOR_BASE_URL=https://api.openai.com/v1

MODELER_API_KEY=sk-xxx
MODELER_MODEL=gpt-4
MODELER_BASE_URL=https://api.openai.com/v1

CODER_API_KEY=sk-xxx
CODER_MODEL=gpt-4
CODER_BASE_URL=https://api.openai.com/v1

WRITER_API_KEY=sk-xxx
WRITER_MODEL=gpt-4
WRITER_BASE_URL=https://api.openai.com/v1

# Workflow Configuration
MAX_CHAT_TURNS=70          # Maximum chat turns per agent
MAX_RETRIES=5              # Maximum retries for code execution

# Code Interpreter
E2B_API_KEY=               # Optional, leave empty for local Jupyter

# Academic Search
OPENALEX_EMAIL=your-email@example.com

# Web Search
TAVILY_API_KEY=tvly-xxx    # Optional
EXA_API_KEY=exa-xxx        # Optional
SEARCH_DEFAULT_PROVIDER=tavily
SEARCH_MAX_RESULTS=10

# System
LOG_LEVEL=DEBUG
DEBUG=true
SERVER_HOST=http://localhost:8000

# Redis (REQUIRED)
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20

# CORS
CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### Model Configuration (`model_config.toml`)
```toml
[config1]
COORDINATOR_API_KEY=''
COORDINATOR_MODEL=''
COORDINATOR_BASE_URL=''

MODELER_API_KEY=''
MODELER_MODEL=''
MODELER_BASE_URL=''

CODER_API_KEY=''
CODER_MODEL=''
CODER_BASE_URL=''

WRITER_API_KEY=''
WRITER_MODEL=''
WRITER_BASE_URL=''

[current]
current = 'config1'
```

#### Prompt Templates (`md_template.toml`, `md_template_en.toml`)
- Customizable prompts for each agent
- Separate templates for Chinese and English
- Support for prompt injection per subtask

### Frontend Configuration

#### Development (`.env.development`)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_APP_TITLE=MathModelAgent
VITE_DEBUG=true
```

#### Production (`.env.production`)
```bash
VITE_API_BASE_URL=https://your-domain.com/api
VITE_WS_BASE_URL=wss://your-domain.com/ws
VITE_APP_TITLE=MathModelAgent
VITE_DEBUG=false
```

## Supported File Types

### Data Files
- Text: `.txt`, `.md`, `.json`
- Spreadsheet: `.csv`, `.xlsx`
- Code: `.py`, `.r`, `.ipynb`
- Image: `.png`, `.jpg`, `.jpeg`, `.gif`, `.pdf`
- Document: `.docx`, `.pptx`

### Archive Files (Auto-extract)
- `.zip`, `.rar`, `.7z`, `.tar`, `.gz`

## Code Interpreter Types

### Local Interpreter (Default)
- Uses Jupyter kernel
- Saves code as `.ipynb` notebooks
- Direct file system access
- Faster for simple tasks
- No API key required

### Cloud Interpreter (E2B)
- Remote execution environment
- Isolated sandbox
- Better security
- Requires E2B API key
- Set `E2B_API_KEY` in `.env.dev`

## Agent System Details

### CoordinatorAgent
- **Role**: Problem analysis and decomposition
- **Input**: Raw problem description
- **Output**: Structured problem breakdown
- **Recommended Model**: Fast, cost-effective (GPT-3.5, Claude-Haiku)

### ModelerAgent
- **Role**: Mathematical model creation
- **Input**: Problem structure from Coordinator
- **Output**: Mathematical formulation and solution approach
- **Recommended Model**: Strong reasoning (GPT-4, Claude-3-Opus, DeepSeek-R1)

### CoderAgent
- **Role**: Code implementation and debugging
- **Input**: Mathematical model
- **Output**: Executable code with results
- **Features**:
  - Automatic error retry (up to 5 times)
  - Code execution in Jupyter/E2B
  - Real-time output streaming
- **Recommended Model**: Code-specialized (GPT-4, DeepSeek-Coder)

### WriterAgent
- **Role**: Academic paper generation
- **Input**: Modeling results and code output
- **Output**: Formatted paper (Markdown/LaTeX)
- **Features**:
  - Section-by-section generation
  - Literature citation integration
  - Template-based formatting
- **Recommended Model**: Writing-focused (GPT-4, Claude-3)

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
