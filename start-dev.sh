#!/bin/bash

# Nonprofit CRM Development Server Startup Script
# This script starts both the backend API and frontend dev server

echo "🚀 Starting Nonprofit CRM Development Environment..."
echo ""

# Check if Python backend dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if Node modules are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Installing Node dependencies..."
    cd frontend && npm install && cd ..
fi

# Start backend API server in background
echo "📡 Starting Backend API (http://localhost:8000)..."
python api.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "   Waiting for backend to start..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Backend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 10 ]; then
        echo "   ⚠️  Backend might not be responding yet..."
    fi
done

echo ""
echo "🎨 Starting Frontend Dev Server (http://localhost:3000)..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✨ Development environment started!"
echo ""
echo "📋 Service URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "📊 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: (in console above)"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or press Ctrl+C in this terminal"
echo ""

# Wait for user to stop
wait
