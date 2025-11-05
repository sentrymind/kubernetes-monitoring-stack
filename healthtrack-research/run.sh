#!/bin/bash
# HealthTrack Research Startup Script

set -e

echo "💊 HealthTrack Research Startup"
echo "==============================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env and set PUBMED_EMAIL"
    exit 1
fi

# Source environment variables
source .env

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $python_version"

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📥 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Initialize database
echo "🗄️  Initializing database..."
python -c "from backend.database import init_db; init_db()"

echo ""
echo "🚀 Starting HealthTrack Research..."
echo "===================================="
echo "Backend API will start on http://localhost:8000"
echo "Frontend will start on http://localhost:8501"
echo "===================================="
echo ""

# Start backend in background
echo "Starting backend..."
python backend/main.py &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3

# Start frontend
echo "Starting frontend..."
streamlit run frontend/app.py

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null || true
