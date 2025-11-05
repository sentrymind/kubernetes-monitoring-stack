#!/bin/bash

# Research Agent Startup Script

set -e

echo "🔬 Research Agent Startup"
echo "========================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env and set PUBMED_EMAIL to your email address"
    exit 1
fi

# Source environment variables
source .env

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data visualizations logs

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $python_version"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📥 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Pre-download embedding model
echo "🤖 Downloading embedding model (first time only)..."
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL:-all-MiniLM-L6-v2}')" 2>/dev/null || true

# Start the application
echo ""
echo "🚀 Starting Research Agent..."
echo "================================"
echo "Web Interface: http://localhost:${API_PORT:-8000}"
echo "API Docs: http://localhost:${API_PORT:-8000}/docs"
echo "================================"
echo ""

python3 api/main.py
