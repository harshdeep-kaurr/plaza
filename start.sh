#!/bin/bash

# Plaza Application Startup Script

echo "🚀 Starting Plaza Application..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the plaza directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected structure: plaza/{backend,frontend,start.sh}"
    exit 1
fi

# Check for .env file in backend
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env file not found"
    echo "   Please create backend/.env with your API keys:"
    echo "   NEWS_API_KEY=your_key_here"
    echo "   OPENAI_API_KEY=your_key_here (optional)"
    echo "   ANTHROPIC_API_KEY=your_key_here (optional)"
    echo ""
fi

# Function to start backend
start_backend() {
    echo "🔧 Starting backend server..."
    cd backend
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing Python dependencies..."
        pip install -r requirements.txt
    fi
    python app.py &
    BACKEND_PID=$!
    cd ..
    echo "✅ Backend started on http://localhost:5001 (PID: $BACKEND_PID)"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting frontend server..."
    cd frontend
    if [ -f "package.json" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
    fi
    npm start &
    FRONTEND_PID=$!
    cd ..
    echo "✅ Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"
}

# Start both servers
start_backend
sleep 3
start_frontend

echo ""
echo "🎉 Plaza is now running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait