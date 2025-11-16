#!/bin/bash
# MathModelAgent One-Click Startup Script for Linux/macOS
# This script starts both backend and frontend services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Stopping all services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

show_help() {
    echo -e "${CYAN}MathModelAgent Startup Script${NC}"
    echo "Usage: ./start.sh [options]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  docker     Start using Docker Compose"
    echo "  help       Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./start.sh         # Start in local mode"
    echo "  ./start.sh docker  # Start with Docker"
}

if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN} MathModelAgent Startup Script${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

if [ "$1" = "docker" ]; then
    echo -e "${YELLOW}Starting in Docker mode...${NC}"
    echo ""

    # Check Docker
    echo "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Error: Docker is not installed or not in PATH${NC}"
        echo "Please install Docker from https://www.docker.com/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker $(docker --version)${NC}"

    # Check Docker Compose
    echo "Checking Docker Compose..."
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}✗ Error: Docker Compose is not available${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose $(docker compose version)${NC}"

    echo ""
    echo -e "${YELLOW}Starting services with Docker Compose...${NC}"
    docker compose up --build

    exit 0
fi

echo -e "${YELLOW}Starting in Local mode...${NC}"
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Error: Python is not installed or not in PATH${NC}"
    echo "Please install Python 3.12+ from https://www.python.org/"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version)${NC}"

# Check Node.js
echo "[2/5] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Error: Node.js is not installed or not in PATH${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version)${NC}"

# Check Redis
echo "[3/5] Checking Redis status..."
if python3 -c "import redis; r=redis.Redis(host='localhost', port=6379); r.ping()" 2>/dev/null; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Redis is not running or not accessible${NC}"
    echo "Please start Redis manually:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  brew install redis"
        echo "  brew services start redis"
    else
        echo "  sudo apt-get install redis-server  # Ubuntu/Debian"
        echo "  sudo systemctl start redis         # SystemD"
    fi
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check pnpm
echo "[4/5] Checking pnpm installation..."
if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}pnpm not found, installing...${NC}"
    npm install -g pnpm
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to install pnpm${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ pnpm $(pnpm --version)${NC}"

# Setup environment
echo "[5/5] Setting up environment..."

# Install backend dependencies
cd backend
if [ ! -d ".venv" ]; then
    echo "Installing backend dependencies..."
    pip3 install uv > /dev/null 2>&1
    uv sync
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to install backend dependencies${NC}"
        cd ..
        exit 1
    fi
fi
cd ..

# Install frontend dependencies
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    pnpm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to install frontend dependencies${NC}"
        cd ..
        exit 1
    fi
fi
cd ..

echo -e "${GREEN}✓ Environment setup complete${NC}"
echo ""

# Start services
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN} Starting Services${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo "Backend will start on: http://localhost:8000"
echo "Frontend will start on: http://localhost:5173"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Start backend in background
cd backend
source .venv/bin/activate
ENV=DEV uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to initialize
sleep 3

# Start frontend in background
cd frontend
pnpm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}Services are running!${NC}"
echo "Backend logs: tail -f backend.log"
echo "Frontend logs: tail -f frontend.log"
echo ""

# Wait for user interrupt
wait
