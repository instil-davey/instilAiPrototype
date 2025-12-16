#!/bin/bash

echo "======================================"
echo "  Nonprofit CRM - Startup Script"
echo "======================================"
echo ""

# Configure dotenv usage flag
USE_DOTENV=false
if [ -f ".env" ]; then
    USE_DOTENV=true
fi

OPENVOICE_PID=""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✓ Python is installed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Determine dotenv runner now that venv exists
DOTENV_RUN=""
if [ "$USE_DOTENV" = true ]; then
    echo "Loading backend environment from .env via python-dotenv..."
    DOTENV_RUN="venv/bin/python -m dotenv run --"
fi

# Check if we should auto-start an OpenVoice server
OPENVOICE_COMMAND=""
if [ "$USE_DOTENV" = true ]; then
    OPENVOICE_COMMAND=$(venv/bin/python - <<'PY'
from dotenv import dotenv_values
print(dotenv_values('.env').get('OPENVOICE_SERVER_COMMAND', ''))
PY
    )
fi

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -q -r requirements.txt

# Generate sample data if database doesn't exist
if [ ! -f "nonprofit_crm.db" ]; then
    echo ""
    echo "No database found. Generating sample data..."
    if [ -n "$DOTENV_RUN" ]; then
        $DOTENV_RUN venv/bin/python generate_sample_data.py
    else
        venv/bin/python generate_sample_data.py
    fi
fi

# Optional OpenVoice server launch
if [ -n "$OPENVOICE_COMMAND" ]; then
    echo ""
    echo "======================================"
    echo "  Starting OpenVoice Server"
    echo "======================================"
    echo ""
    echo "Command: $OPENVOICE_COMMAND"
    bash -c "$OPENVOICE_COMMAND" &
    OPENVOICE_PID=$!
    sleep 2
fi

echo ""
echo "======================================"
echo "  Starting Backend Server"
echo "======================================"
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "API Documentation at: http://localhost:8000/docs"
echo ""

# Start backend in background
if [ -n "$DOTENV_RUN" ]; then
    $DOTENV_RUN venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000 &
else
    venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000 &
fi
BACKEND_PID=$!
cleanup_cmd="kill $BACKEND_PID 2>/dev/null"
if [ -n "$OPENVOICE_PID" ]; then
    cleanup_cmd="$cleanup_cmd; kill $OPENVOICE_PID 2>/dev/null"
fi
trap "$cleanup_cmd" EXIT

# Wait for backend to start
sleep 3

# Check if frontend directory exists
if [ -d "frontend" ]; then
    echo ""
    echo "======================================"
    echo "  Starting Frontend Server"
    echo "======================================"
    echo ""

    cd frontend

    # Install frontend dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi

    echo ""
    echo "Frontend will be available at: http://localhost:5173 (or your configured port)"
    echo ""
    echo "Default login credentials:"
    echo "  Username: admin"
    echo "  Password: secret"
    echo ""
    echo "======================================"
    echo "  CRM is ready!"
    echo "======================================"
    echo ""

    # Start frontend
    npm run dev
else
    echo "Frontend directory not found. Running backend only."
    wait $BACKEND_PID
fi

# Cleanup handled by trap above
