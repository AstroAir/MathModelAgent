#!/usr/bin/env pwsh
# MathModelAgent One-Click Startup Script for Windows PowerShell
# This script starts both backend and frontend services

param(
    [switch]$Docker,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColorOutput "MathModelAgent Startup Script" "Cyan"
    Write-ColorOutput "Usage: .\start.ps1 [options]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Options:" "Yellow"
    Write-ColorOutput "  -Docker    Start using Docker Compose" "White"
    Write-ColorOutput "  -Help      Show this help message" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Examples:" "Yellow"
    Write-ColorOutput "  .\start.ps1           # Start in local mode" "White"
    Write-ColorOutput "  .\start.ps1 -Docker   # Start with Docker" "White"
}

if ($Help) {
    Show-Help
    exit 0
}

Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput " MathModelAgent Startup Script" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput ""

if ($Docker) {
    Write-ColorOutput "Starting in Docker mode..." "Yellow"
    Write-ColorOutput ""

    # Check Docker
    Write-ColorOutput "Checking Docker installation..." "White"
    try {
        $dockerVersion = docker --version
        Write-ColorOutput "✓ $dockerVersion" "Green"
    } catch {
        Write-ColorOutput "✗ Error: Docker is not installed or not in PATH" "Red"
        Write-ColorOutput "Please install Docker from https://www.docker.com/" "Red"
        exit 1
    }

    # Check Docker Compose
    Write-ColorOutput "Checking Docker Compose..." "White"
    try {
        $composeVersion = docker compose version
        Write-ColorOutput "✓ $composeVersion" "Green"
    } catch {
        Write-ColorOutput "✗ Error: Docker Compose is not available" "Red"
        exit 1
    }

    Write-ColorOutput ""
    Write-ColorOutput "Starting services with Docker Compose..." "Yellow"
    docker compose up --build

    exit 0
}

Write-ColorOutput "Starting in Local mode..." "Yellow"
Write-ColorOutput ""

# Check Python
Write-ColorOutput "[1/5] Checking Python installation..." "White"
try {
    $pythonVersion = python --version 2>&1
    Write-ColorOutput "✓ $pythonVersion" "Green"
} catch {
    Write-ColorOutput "✗ Error: Python is not installed or not in PATH" "Red"
    Write-ColorOutput "Please install Python 3.12+ from https://www.python.org/" "Red"
    exit 1
}

# Check Node.js
Write-ColorOutput "[2/5] Checking Node.js installation..." "White"
try {
    $nodeVersion = node --version 2>&1
    Write-ColorOutput "✓ Node.js $nodeVersion" "Green"
} catch {
    Write-ColorOutput "✗ Error: Node.js is not installed or not in PATH" "Red"
    Write-ColorOutput "Please install Node.js from https://nodejs.org/" "Red"
    exit 1
}

# Check Redis
Write-ColorOutput "[3/5] Checking Redis status..." "White"
try {
    $redisTest = python -c "import redis; r=redis.Redis(host='localhost', port=6379); r.ping()" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✓ Redis is running" "Green"
    } else {
        throw
    }
} catch {
    Write-ColorOutput "⚠ Warning: Redis is not running or not accessible" "Yellow"
    Write-ColorOutput "Please start Redis manually or install it from:" "Yellow"
    Write-ColorOutput "https://github.com/microsoftarchive/redis/releases" "Yellow"
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Check pnpm
Write-ColorOutput "[4/5] Checking pnpm installation..." "White"
try {
    $pnpmVersion = pnpm --version 2>&1
    Write-ColorOutput "✓ pnpm $pnpmVersion" "Green"
} catch {
    Write-ColorOutput "pnpm not found, installing..." "Yellow"
    npm install -g pnpm
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "✗ Failed to install pnpm" "Red"
        exit 1
    }
}

# Setup environment
Write-ColorOutput "[5/5] Setting up environment..." "White"

# Install backend dependencies
Push-Location backend
if (-not (Test-Path ".venv")) {
    Write-ColorOutput "Installing backend dependencies..." "Yellow"
    pip install uv | Out-Null
    uv sync
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "✗ Failed to install backend dependencies" "Red"
        Pop-Location
        exit 1
    }
}
Pop-Location

# Install frontend dependencies
Push-Location frontend
if (-not (Test-Path "node_modules")) {
    Write-ColorOutput "Installing frontend dependencies..." "Yellow"
    pnpm install
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "✗ Failed to install frontend dependencies" "Red"
        Pop-Location
        exit 1
    }
}
Pop-Location

Write-ColorOutput "✓ Environment setup complete" "Green"
Write-ColorOutput ""

# Start services
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput " Starting Services" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput ""
Write-ColorOutput "Backend will start on: http://localhost:8000" "White"
Write-ColorOutput "Frontend will start on: http://localhost:5173" "White"
Write-ColorOutput ""
Write-ColorOutput "Press Ctrl+C to stop all services" "Yellow"
Write-ColorOutput ""

# Create job tracking
$jobs = @()

# Start backend
$backendScript = {
    Set-Location backend
    & .\.venv\Scripts\Activate.ps1
    $env:ENV = "DEV"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120
}
$backendJob = Start-Job -ScriptBlock $backendScript -Name "Backend"
$jobs += $backendJob
Write-ColorOutput "✓ Backend starting (Job ID: $($backendJob.Id))" "Green"

# Wait for backend to initialize
Start-Sleep -Seconds 3

# Start frontend
$frontendScript = {
    Set-Location frontend
    pnpm run dev
}
$frontendJob = Start-Job -ScriptBlock $frontendScript -Name "Frontend"
$jobs += $frontendJob
Write-ColorOutput "✓ Frontend starting (Job ID: $($frontendJob.Id))" "Green"

Write-ColorOutput ""
Write-ColorOutput "Services are starting..." "Green"
Write-ColorOutput ""

# Monitor jobs
try {
    while ($true) {
        foreach ($job in $jobs) {
            $output = Receive-Job -Job $job
            if ($output) {
                Write-Host "[$($job.Name)] $output"
            }

            if ($job.State -eq "Failed" -or $job.State -eq "Stopped") {
                Write-ColorOutput "✗ $($job.Name) has stopped" "Red"
            }
        }
        Start-Sleep -Seconds 1
    }
} finally {
    Write-ColorOutput ""
    Write-ColorOutput "Stopping all services..." "Yellow"
    $jobs | Stop-Job
    $jobs | Remove-Job -Force
    Write-ColorOutput "✓ All services stopped" "Green"
}
