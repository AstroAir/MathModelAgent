@echo off
REM MathModelAgent One-Click Startup Script for Windows
REM This script starts both backend and frontend services

setlocal enabledelayedexpansion

echo ========================================
echo  MathModelAgent Startup Script
echo ========================================
echo.

REM Color codes
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "NC=[0m"

REM Check if running in Docker mode
set "DOCKER_MODE=false"
if "%1"=="docker" set "DOCKER_MODE=true"

if "%DOCKER_MODE%"=="true" (
    echo %YELLOW%Starting in Docker mode...%NC%
    goto :docker_mode
)

echo %YELLOW%Starting in Local mode...%NC%
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Python is not installed or not in PATH%NC%
    echo Please install Python 3.12+ from https://www.python.org/
    pause
    exit /b 1
)
echo %GREEN%✓ Python found%NC%

REM Check Node.js installation
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Node.js is not installed or not in PATH%NC%
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo %GREEN%✓ Node.js found%NC%

REM Check Redis installation
echo [3/5] Checking Redis status...
REM Try to connect to Redis
python -c "import redis; r=redis.Redis(host='localhost', port=6379); r.ping()" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%Warning: Redis is not running or not accessible%NC%
    echo Please start Redis manually or install it from:
    echo https://github.com/microsoftarchive/redis/releases
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "!continue!"=="y" (
        exit /b 1
    )
) else (
    echo %GREEN%✓ Redis is running%NC%
)

REM Check pnpm installation
echo [4/5] Checking pnpm installation...
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%pnpm not found, installing...%NC%
    npm install -g pnpm
    if errorlevel 1 (
        echo %RED%Failed to install pnpm%NC%
        pause
        exit /b 1
    )
)
echo %GREEN%✓ pnpm found%NC%

REM Setup environment
echo [5/5] Setting up environment...

REM Install backend dependencies
cd backend
if not exist ".venv" (
    echo Installing backend dependencies...
    pip install uv >nul 2>&1
    uv sync
    if errorlevel 1 (
        echo %RED%Failed to install backend dependencies%NC%
        cd ..
        pause
        exit /b 1
    )
)
cd ..

REM Install frontend dependencies
cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    pnpm install
    if errorlevel 1 (
        echo %RED%Failed to install frontend dependencies%NC%
        cd ..
        pause
        exit /b 1
    )
)
cd ..

echo %GREEN%✓ Environment setup complete%NC%
echo.

REM Start services
echo ========================================
echo  Starting Services
echo ========================================
echo.
echo Backend will start on: http://localhost:8000
echo Frontend will start on: http://localhost:5173
echo.
echo Press Ctrl+C to stop all services
echo.

REM Start backend in new window
start "MathModelAgent - Backend" cmd /k "cd backend && .venv\Scripts\activate.bat && set ENV=DEV && uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "MathModelAgent - Frontend" cmd /k "cd frontend && pnpm run dev"

echo.
echo %GREEN%Services are starting...%NC%
echo Check the new windows for logs
echo.
echo To stop all services, close the terminal windows
echo.
pause
exit /b 0

:docker_mode
echo.
echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Docker is not installed or not in PATH%NC%
    echo Please install Docker from https://www.docker.com/
    pause
    exit /b 1
)
echo %GREEN%✓ Docker found%NC%

echo Checking Docker Compose...
docker compose version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Docker Compose is not available%NC%
    pause
    exit /b 1
)
echo %GREEN%✓ Docker Compose found%NC%

echo.
echo Starting services with Docker Compose...
docker compose up --build

exit /b 0
