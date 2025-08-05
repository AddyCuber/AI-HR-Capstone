#!/bin/bash

echo "🚀 Resume AI Matcher Pro - Setup Script"
echo "========================================"

# Check if Docker is installed
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker and Docker Compose found"
    DOCKER_AVAILABLE=true
else
    echo "⚠️  Docker not found. Will use local development setup."
    DOCKER_AVAILABLE=false
fi

# Check if Python is installed
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found"
    PYTHON_AVAILABLE=true
else
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check if Node.js is installed
if command -v node &> /dev/null; then
    echo "✅ Node.js found"
    NODE_AVAILABLE=true
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo ""
echo "Choose your setup method:"
echo "1. Docker (recommended)"
echo "2. Local development"
echo "3. Backend only"
echo "4. Frontend only"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        if [ "$DOCKER_AVAILABLE" = true ]; then
            echo "🐳 Setting up with Docker..."
            
            # Create .env file if it doesn't exist
            if [ ! -f .env ]; then
                echo "Creating .env file..."
                cat > .env << EOF
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL_PROVIDER=mistral
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
                echo "⚠️  Please edit .env file with your API keys before running"
            fi
            
            echo "Building and starting containers..."
            docker-compose up --build -d
            
            echo ""
            echo "🎉 Setup complete!"
            echo "Frontend: http://localhost:3000"
            echo "Backend: http://localhost:8000"
            echo "API Docs: http://localhost:8000/docs"
        else
            echo "❌ Docker not available. Please install Docker and Docker Compose first."
            exit 1
        fi
        ;;
    2)
        echo "🔧 Setting up local development..."
        
        # Backend setup
        echo "Setting up backend..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        
        # Create .env file for backend
        if [ ! -f .env ]; then
            cat > .env << EOF
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL_PROVIDER=mistral
EOF
            echo "⚠️  Please edit backend/.env file with your API keys"
        fi
        
        echo "✅ Backend setup complete"
        cd ..
        
        # Frontend setup
        echo "Setting up frontend..."
        cd frontend
        npm install
        
        # Create .env.local file for frontend
        if [ ! -f .env.local ]; then
            echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
        fi
        
        echo "✅ Frontend setup complete"
        cd ..
        
        echo ""
        echo "🎉 Local development setup complete!"
        echo ""
        echo "To start the application:"
        echo "1. Start backend: cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
        echo "2. Start frontend: cd frontend && npm run dev"
        echo ""
        echo "Frontend: http://localhost:3000"
        echo "Backend: http://localhost:8000"
        ;;
    3)
        echo "🔧 Setting up backend only..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        
        if [ ! -f .env ]; then
            cat > .env << EOF
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL_PROVIDER=mistral
EOF
            echo "⚠️  Please edit .env file with your API keys"
        fi
        
        echo "✅ Backend setup complete"
        echo "To start: source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
        cd ..
        ;;
    4)
        echo "🔧 Setting up frontend only..."
        cd frontend
        npm install
        
        if [ ! -f .env.local ]; then
            echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
        fi
        
        echo "✅ Frontend setup complete"
        echo "To start: npm run dev"
        cd ..
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 Next steps:"
echo "1. Edit the .env file(s) with your API keys"
echo "2. Start the application using the provided commands"
echo "3. Open your browser and navigate to the frontend URL"
echo ""
echo "📖 For more information, see README.md" 