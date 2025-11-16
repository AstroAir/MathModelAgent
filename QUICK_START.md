# Quick Start Guide

Get MathModelAgent up and running in minutes!

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed ([Download](https://www.python.org/downloads/))
- **Node.js 20+** installed ([Download](https://nodejs.org/))
- **Redis** running ([Installation guides below](#installing-redis))
- **Git** for cloning the repository

## Installation Methods

Choose the method that works best for you:

### 🐳 Method 1: Docker (Recommended - Easiest)

**Pros:** No need to install dependencies manually, isolated environment

**Requirements:** Docker and Docker Compose

```bash
# 1. Clone the repository
git clone https://github.com/jihe520/MathModelAgent.git
cd MathModelAgent

# 2. Start everything with one command
docker-compose up

# That's it! Access the app at http://localhost:5173
```

### 🚀 Method 2: One-Click Scripts (Fast)

**Pros:** Automated setup, checks dependencies

**Windows:**

```cmd
# Clone the repository
git clone https://github.com/jihe520/MathModelAgent.git
cd MathModelAgent

# Run the startup script
start.bat

# Or use PowerShell
.\start.ps1
```

**Linux/macOS:**

```bash
# Clone the repository
git clone https://github.com/jihe520/MathModelAgent.git
cd MathModelAgent

# Make the script executable
chmod +x start.sh

# Run it
./start.sh
```

### 💻 Method 3: Manual Setup (Full Control)

**Pros:** Complete control over the setup process

#### Step 1: Install Redis

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**

```bash
brew install redis
brew services start redis
```

**Windows:**

Download from [GitHub Releases](https://github.com/microsoftarchive/redis/releases) or use WSL.

#### Step 2: Backend Setup

```bash
cd backend

# Install uv (recommended)
pip install uv

# Install dependencies
uv sync

# Activate virtual environment
# On Windows:
.venv\Scripts\activate.bat
# On Linux/macOS:
source .venv/bin/activate

# Start the backend
# On Windows:
set ENV=DEV
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# On Linux/macOS:
ENV=DEV uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 3: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install pnpm if not already installed
npm install -g pnpm

# Install dependencies
pnpm install

# Start the frontend
pnpm run dev
```

## Configuration

### API Keys

After starting the application:

1. Open <http://localhost:5173>
2. Click on the profile icon in the sidebar
3. Navigate to **Settings** → **API Keys**
4. Add your LLM provider API keys:
   - OpenAI API Key
   - Anthropic API Key (optional)
   - Or any other supported provider

### Environment Variables

Edit the configuration files:

**Backend** (`backend/.env.dev`):

```env
# Redis connection
REDIS_URL=redis://localhost:6379/0

# Environment
ENV=DEV

# Code interpreter settings
CODE_INTERPRETER_TYPE=local  # or 'e2b' for cloud

# E2B API key (if using cloud interpreter)
E2B_API_KEY=your_key_here
```

**Frontend** (`frontend/.env.development`):

```env
# API endpoint
VITE_API_BASE_URL=http://localhost:8000
```

## Verification

Check if everything is working:

1. **Backend**: Visit <http://localhost:8000/docs> to see the API documentation
2. **Frontend**: Visit <http://localhost:5173> to use the web interface
3. **Redis**: Run `redis-cli ping` - should return `PONG`

## Common Issues

### Redis Connection Failed

**Error:** `Redis connection refused`

**Solution:**

```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis:
# Ubuntu/Debian:
sudo systemctl start redis

# macOS:
brew services start redis

# Windows: Start redis-server.exe manually
```

### Port Already in Use

**Error:** `Port 8000/5173 already in use`

**Solution:**

```bash
# Find and kill the process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:8000 | xargs kill -9
```

### Python Virtual Environment Issues

**Error:** `Command 'python' not found` or `No module named 'uvicorn'`

**Solution:**

```bash
# Make sure you activated the virtual environment
# Windows:
backend\.venv\Scripts\activate.bat

# Linux/macOS:
source backend/.venv/bin/activate

# Verify activation (you should see (.venv) in your prompt)
```

### Node.js Version Issues

**Error:** `Node version not supported`

**Solution:**

```bash
# Check your Node.js version
node --version

# Should be v20 or higher. If not, update Node.js
```

## Next Steps

Now that you're set up:

1. **Try a sample problem**: Input a mathematical modeling problem
2. **Explore features**: Check out the different agent modes
3. **Read the docs**: See [README.md](README.md) for detailed documentation
4. **Join the community**: Get help in our [QQ Group](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=rFKquDTSxKcWpEhRgpJD-dPhTtqLwJ9r) or [Discord](https://discord.gg/3Jmpqg5J)

## Development

If you want to contribute:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Look for `good first issue` labels on GitHub

## Additional Resources

- **Full Documentation**: [README.md](README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **API Docs**: <http://localhost:8000/docs> (when running)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/jihe520/MathModelAgent/issues)
- **QQ Group**: 699970403
- **Discord**: [Join our server](https://discord.gg/3Jmpqg5J)
- **DeepWiki**: [Project Wiki](https://deepwiki.com/jihe520/MathModelAgent)

---

**Happy modeling!** 🎉
