#!/bin/bash

# Legal Document AI Simplifier - Startup Script
# This script helps you get started with the application

echo "⚖️  Legal Document AI Simplifier"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp env_example.txt .env
    echo "📝 Please edit .env file with your OpenAI API key"
    echo "   You can get one from: https://platform.openai.com/api-keys"
    echo ""
    echo "Press Enter when you've updated the .env file..."
    read
fi

# Check if OpenAI API key is set
if ! grep -q "your_openai_api_key_here" .env; then
    echo "✅ OpenAI API key configured"
else
    echo "❌ Please set your OpenAI API key in the .env file"
    exit 1
fi

echo ""
echo "🚀 Starting the application..."
echo ""
echo "Choose your interface:"
echo "1. Flask Web App (http://localhost:5000)"
echo "2. Streamlit App (http://localhost:8501)"
echo "3. Run tests"
echo "4. Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🌐 Starting Flask web application..."
        echo "Open your browser and go to: http://localhost:5000"
        echo "Press Ctrl+C to stop the server"
        python app.py
        ;;
    2)
        echo "📊 Starting Streamlit application..."
        echo "Open your browser and go to: http://localhost:8501"
        echo "Press Ctrl+C to stop the server"
        streamlit run streamlit_app.py
        ;;
    3)
        echo "🧪 Running tests..."
        python test_app.py
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
