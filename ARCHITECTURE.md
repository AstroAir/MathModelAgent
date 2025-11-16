# MathModelAgent Architecture

This document provides a comprehensive overview of the MathModelAgent system architecture, design decisions, and technical implementation details.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Deployment Architecture](#deployment-architecture)

## System Overview

MathModelAgent is an AI-powered system designed to automate the mathematical modeling process, from problem analysis to paper generation. The system employs a multi-agent architecture where specialized agents collaborate to solve complex mathematical modeling tasks.

### Key Features

- **Multi-Agent System**: Specialized agents for different tasks (modeling, coding, writing)
- **Code Interpreter**: Local and cloud-based code execution environments
- **LLM Integration**: Support for multiple language models via LiteLLM
- **Real-time Communication**: WebSocket-based bidirectional communication
- **Document Generation**: Automated paper writing with proper formatting

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Vue.js    │  │   Pinia     │  │  WebSocket  │        │
│  │  UI Layer   │  │State Manager│  │   Client    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                      API Gateway Layer                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │   │
│  │  │   REST   │  │WebSocket │  │  Authentication  │  │   │
│  │  │   API    │  │ Handler  │  │   & CORS        │  │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     Business Logic Layer                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Multi-Agent Orchestration                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │
│  │  │ Modeling │  │  Coding  │  │     Writing      │   │  │
│  │  │  Agent   │  │  Agent   │  │      Agent       │   │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │  │
│  │                                                       │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │         Workflow Coordination Engine          │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Service Layer                            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐   │  │
│  │  │    LLM     │  │    Code    │  │   Document   │   │  │
│  │  │  Service   │  │ Interpreter│  │  Generator   │   │  │
│  │  └────────────┘  └────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Infrastructure Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Jupyter │  │   File   │  │  E2B/    │   │
│  │  Cache   │  │  Kernel  │  │  System  │  │ Daytona  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │   LLM Providers  │  │    Literature Search APIs      │  │
│  │  (OpenAI, etc.)  │  │   (Semantic Scholar, etc.)     │  │
│  └──────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Vue.js + TypeScript)

**Location**: `/frontend`

The frontend is built with Vue 3 using the Composition API and TypeScript for type safety.

#### Key Components

- **UI Components** (`/src/components`): Reusable Vue components using Reka UI
- **Pages** (`/src/pages`): Main application pages (Chat, Task, Coder, Writer)
- **State Management** (`/src/stores`): Pinia stores for global state
- **API Client** (`/src/apis`): Axios-based API communication layer
- **Routing**: Vue Router for navigation

#### Technologies

- **Vue 3**: Progressive JavaScript framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Pinia**: State management
- **TailwindCSS**: Utility-first CSS framework
- **Reka UI**: Accessible component library
- **Marked**: Markdown rendering
- **KaTeX**: LaTeX math rendering

### Backend (FastAPI + Python)

**Location**: `/backend`

The backend is built with FastAPI, providing a high-performance async API.

#### Key Modules

**1. API Layer** (`/app/api`)

- REST endpoints for CRUD operations
- WebSocket handlers for real-time communication
- Request/response models with Pydantic

**2. Core Layer** (`/app/core`)

- Business logic implementation
- Multi-agent orchestration
- Workflow management

**3. Agents** (`/app/agents`)

- **Modeling Agent**: Analyzes problems and creates mathematical models
- **Coding Agent**: Implements models in code and runs simulations
- **Writing Agent**: Generates academic papers with proper formatting

**4. Services** (`/app/services`)

- **LLM Service**: Manages interactions with language models via LiteLLM
- **Code Interpreter**: Executes Python code in isolated environments
- **Document Generator**: Creates formatted documents

**5. Configuration** (`/app/config`)

- Environment settings
- Prompt templates
- Model configurations

#### Technologies

- **FastAPI**: Modern async web framework
- **Pydantic**: Data validation using Python type annotations
- **LiteLLM**: Unified interface for multiple LLM providers
- **Redis**: Caching and session storage
- **Jupyter**: Code execution kernel
- **Celery**: Asynchronous task queue (for background jobs)

### Multi-Agent System

The system employs a workflow-based agent orchestration:

```python
# Agent workflow
Problem Input → Modeling Agent → Mathematical Model
                     ↓
            Coding Agent → Code Implementation
                     ↓
            Execute & Debug → Results
                     ↓
            Writing Agent → Final Paper
```

#### Agent Communication

- **Agentless Workflow**: Direct sequential processing without complex agent frameworks
- **Context Sharing**: Agents share context through a common workspace
- **Hand-off Mechanism**: Results from one agent are passed to the next
- **Error Handling**: Failed tasks can be retried or handed off to more capable models

### Code Interpreter

Two execution modes are supported:

**1. Local Interpreter**

- Uses Jupyter kernel for code execution
- Saves code in `.ipynb` format for easy editing
- Direct access to local file system
- Faster execution for simple tasks

**2. Cloud Interpreter**

- Integrates with E2B and Daytona
- Isolated execution environment
- Better security for untrusted code
- Scalable execution

## Data Flow

### Task Execution Flow

1. **User Input**: User submits a mathematical modeling problem
2. **Task Creation**: System creates a new task and workspace
3. **Problem Analysis**: Modeling agent analyzes the problem
4. **Model Development**: Agent creates mathematical formulation
5. **Code Generation**: Coding agent implements the model
6. **Execution**: Code runs in interpreter (local or cloud)
7. **Debugging**: If errors occur, coding agent fixes them
8. **Paper Writing**: Writing agent creates formatted document
9. **Result Delivery**: Final outputs are saved and presented to user

### WebSocket Communication

```
Client                    Server
  │                         │
  ├──── Connect ───────────>│
  │<──── Connected ─────────┤
  │                         │
  ├──── Start Task ────────>│
  │                         ├─── Process
  │<──── Status Update ─────┤
  │<──── Progress Update ───┤
  │<──── Code Output ───────┤
  │                         │
  │<──── Task Complete ─────┤
  │                         │
```

### File Organization

Generated files are organized in workspaces:

```
backend/project/work_dir/
  └── {task_id}/
      ├── notebook.ipynb    # Code execution history
      ├── res.md           # Final result in Markdown
      ├── data/            # Data files
      └── figures/         # Generated plots
```

## Technology Stack

### Frontend Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Framework | Vue 3 | UI framework |
| Language | TypeScript | Type-safe development |
| Build Tool | Vite | Fast builds and HMR |
| State Management | Pinia | Global state |
| Routing | Vue Router | Navigation |
| Styling | TailwindCSS | Utility-first CSS |
| Components | Reka UI | Accessible components |
| Markdown | Marked + KaTeX | Content rendering |
| HTTP Client | Axios | API communication |

### Backend Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Framework | FastAPI | Web API framework |
| Language | Python 3.12+ | Backend language |
| Validation | Pydantic | Data validation |
| ORM/Cache | Redis | Session & cache |
| LLM Interface | LiteLLM | Multi-provider LLM access |
| Code Execution | Jupyter + E2B | Code interpreter |
| Task Queue | Celery | Background tasks |
| Documentation | Pandoc | Document conversion |

### Infrastructure

| Category | Technology | Purpose |
|----------|-----------|---------|
| Containerization | Docker | Application packaging |
| Orchestration | Docker Compose | Multi-container deployment |
| Reverse Proxy | Nginx (optional) | Production deployment |
| CI/CD | GitHub Actions | Automated testing & deployment |

## Design Patterns

### 1. Dependency Injection

FastAPI's dependency injection system is used throughout:

```python
from fastapi import Depends
from app.core.config import get_settings

async def get_task_service(
    settings: Settings = Depends(get_settings)
) -> TaskService:
    return TaskService(settings)

@router.post("/tasks")
async def create_task(
    service: TaskService = Depends(get_task_service)
):
    return await service.create_task()
```

### 2. Repository Pattern

Data access is abstracted through repositories:

```python
class TaskRepository:
    async def create(self, task: Task) -> Task:
        # Save to database/storage
        pass

    async def get(self, task_id: str) -> Optional[Task]:
        # Retrieve from storage
        pass
```

### 3. Service Layer

Business logic is encapsulated in services:

```python
class ModelingService:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def analyze_problem(self, problem: str) -> ModelAnalysis:
        # Complex business logic
        pass
```

### 4. Strategy Pattern

Different LLM providers are handled through a strategy pattern:

```python
class LLMStrategy(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str:
        pass

class OpenAIStrategy(LLMStrategy):
    async def complete(self, prompt: str) -> str:
        # OpenAI specific implementation
        pass
```

### 5. Observer Pattern

WebSocket connections use the observer pattern for real-time updates:

```python
class TaskObserver:
    async def on_progress(self, progress: float):
        await websocket.send_json({"type": "progress", "value": progress})
```

## Deployment Architecture

### Development Mode

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │     │   Backend    │     │    Redis     │
│  (Vite Dev)  │────>│  (Uvicorn)   │────>│   (Local)    │
│ localhost:   │     │ localhost:   │     │ localhost:   │
│   5173       │     │   8000       │     │   6379       │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Docker Deployment

```
┌─────────────────────────────────────────────────────┐
│              Docker Compose Network                  │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Frontend │  │ Backend  │  │      Redis       │  │
│  │Container │  │Container │  │    Container     │  │
│  │          │  │          │  │                  │  │
│  │ Port:    │  │ Port:    │  │ Internal Port:   │  │
│  │  5173    │  │  8000    │  │      6379        │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Production Deployment (Recommended)

```
                    ┌─────────────┐
Internet ──────────>│   Nginx     │
                    │ (Reverse    │
                    │  Proxy)     │
                    └──────┬──────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
    ┌───────▼────────┐           ┌────────▼───────┐
    │   Frontend     │           │    Backend     │
    │   (Static)     │           │  (FastAPI +    │
    │                │           │   Gunicorn)    │
    └────────────────┘           └────────┬───────┘
                                          │
                                 ┌────────▼───────┐
                                 │   Redis        │
                                 │  (Persistent)  │
                                 └────────────────┘
```

## Security Considerations

### API Security

- **CORS**: Configured to allow only specific origins
- **Rate Limiting**: Prevents abuse of API endpoints
- **Input Validation**: All inputs validated with Pydantic
- **API Keys**: LLM API keys stored in environment variables

### Code Execution Security

- **Sandboxing**: Code runs in isolated Jupyter kernels or cloud environments
- **Timeout**: Execution time limits prevent infinite loops
- **Resource Limits**: Memory and CPU usage restrictions
- **No Network Access**: Code execution environments have limited network access

### Data Privacy

- **Session Isolation**: Each user's data is isolated
- **Temporary Storage**: Generated files can be configured to auto-delete
- **No Data Logging**: User inputs are not logged to external services

## Performance Optimization

### Frontend Optimization

- **Code Splitting**: Lazy loading of routes and components
- **Asset Optimization**: Minification and compression
- **Caching**: Browser caching for static assets
- **Lazy Loading**: Images and components loaded on demand

### Backend Optimization

- **Async I/O**: FastAPI's async capabilities for concurrent requests
- **Redis Caching**: Frequently accessed data cached
- **Connection Pooling**: Reuse of database/Redis connections
- **Background Tasks**: Long-running tasks moved to Celery

### Code Execution Optimization

- **Kernel Reuse**: Jupyter kernels are reused when possible
- **Result Caching**: Identical code executions can be cached
- **Parallel Execution**: Multiple code blocks can run concurrently

## Monitoring and Logging

### Logging Strategy

- **Structured Logging**: Using Loguru for structured logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic log file rotation
- **Error Tracking**: Critical errors can be sent to monitoring services

### Metrics

- **Request Metrics**: API endpoint usage and response times
- **Task Metrics**: Success rates, execution times
- **Resource Metrics**: Memory, CPU usage
- **LLM Metrics**: Token usage, costs

## Future Architecture Considerations

### Planned Improvements

1. **Database Integration**: Move from file-based to database storage
2. **Load Balancing**: Support for horizontal scaling
3. **Caching Layer**: CDN for static assets
4. **Message Queue**: RabbitMQ or Kafka for better task management
5. **Microservices**: Split monolith into microservices
6. **API Versioning**: Support multiple API versions
7. **GraphQL**: Alternative to REST API
8. **Kubernetes**: Container orchestration for large deployments

## Conclusion

MathModelAgent's architecture is designed for:

- **Modularity**: Clear separation of concerns
- **Scalability**: Horizontal and vertical scaling capabilities
- **Maintainability**: Clean code and documented patterns
- **Extensibility**: Easy to add new agents and features
- **Performance**: Async operations and caching
- **Security**: Input validation and sandboxed execution

For more information, see:

- [Contributing Guide](CONTRIBUTING.md)
- [API Documentation](http://localhost:8000/docs)
- [Deployment Guide](docs/md/tutorial.md)
