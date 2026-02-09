#!/bin/bash

# Quick Start Script for Cambodia Property Explainer

echo "🏠 Cambodia Property Explainer - Quick Start"
echo "============================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your OpenAI API key:"
    echo ""
    echo "OPENAI_API_KEY=your_key_here"
    echo "MODEL=gpt-4o-mini"
    echo ""
    exit 1
fi

# Check if venv exists (in root or backend folder)
if [ -d "venv" ]; then
    VENV_PATH="venv"
elif [ -d "backend/venv" ]; then
    VENV_PATH="backend/venv"
else
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    VENV_PATH="venv"
    echo "✅ Virtual environment created at venv"
fi

echo "✅ Virtual environment found at $VENV_PATH"

# Activate virtual environment
source $VENV_PATH/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "Installing dependencies..."
    pip install -r backend/requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "✅ Setup complete!"
echo ""

# Kill any existing processes on ports 8001 and 8000
echo "🔍 Checking for existing processes..."
if lsof -ti:8001 > /dev/null 2>&1; then
    echo "Killing existing process on port 8001..."
    kill -9 $(lsof -ti:8001) 2>/dev/null || true
fi
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Killing existing process on port 8000..."
    kill -9 $(lsof -ti:8000) 2>/dev/null || true
fi

# Small delay to ensure ports are freed
sleep 1

echo ""
echo "🚀 Starting servers..."
echo ""

# Start backend in background
echo "Starting backend API on port 8001..."
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m uvicorn main:app --reload --port 8001 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend started successfully
if ! lsof -ti:8001 > /dev/null 2>&1; then
    echo "❌ Backend failed to start!"
    echo "Check backend/main.py and requirements"
    exit 1
fi

echo "✅ Backend started on port 8001"

# Start frontend
echo "Starting frontend on port 8000..."
python3 -m http.server 8000 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 2

echo ""
echo "✅ Servers running!"
echo ""
echo "📱 Open in browser:"
echo "   Frontend: http://localhost:8000/index.html"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Servers stopped'; exit" INT
wait
