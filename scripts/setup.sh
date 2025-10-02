#!/bin/bash

# 🚀 Student Learning & Safety Platform Setup Script
# This script sets up the development environment for the platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_success "Node.js found: v$NODE_VERSION"
        
        # Check if version is >= 18
        if [ "$(printf '%s\n' "18.0.0" "$NODE_VERSION" | sort -V | head -n1)" = "18.0.0" ]; then
            print_success "Node.js version is compatible"
        else
            print_error "Node.js version must be >= 18.0.0"
            exit 1
        fi
    else
        print_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm found: v$NPM_VERSION"
    else
        print_error "npm is not installed"
        exit 1
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python found: v$PYTHON_VERSION"
        
        # Check if version is >= 3.11
        if [ "$(printf '%s\n' "3.11.0" "$PYTHON_VERSION" | sort -V | head -n1)" = "3.11.0" ]; then
            print_success "Python version is compatible"
        else
            print_warning "Python version should be >= 3.11.0 for best compatibility"
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.11+ from https://python.org/"
        exit 1
    fi
    
    # Check pip
    if command_exists pip3; then
        PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
        print_success "pip found: v$PIP_VERSION"
    else
        print_error "pip is not installed"
        exit 1
    fi
    
    # Check Git
    if command_exists git; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_success "Git found: v$GIT_VERSION"
    else
        print_error "Git is not installed. Please install Git from https://git-scm.com/"
        exit 1
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker found: v$DOCKER_VERSION"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker is not installed. You can still run the project manually."
        DOCKER_AVAILABLE=false
    fi
    
    # Check Docker Compose (optional)
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        print_success "Docker Compose is available"
        DOCKER_COMPOSE_AVAILABLE=true
    else
        print_warning "Docker Compose is not available"
        DOCKER_COMPOSE_AVAILABLE=false
    fi
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
            print_warning "Please edit .env file with your actual configuration values"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_warning ".env file already exists, skipping creation"
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Backend dependencies installed"
    
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    print_success "Frontend dependencies installed"
    
    # Create frontend environment file
    if [ ! -f ".env.local" ]; then
        echo "VITE_API_URL=http://localhost:8000" > .env.local
        print_success "Created frontend .env.local file"
    else
        print_warning "Frontend .env.local file already exists"
    fi
    
    cd ..
}

# Function to setup database (if Docker is available)
setup_database() {
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_COMPOSE_AVAILABLE" = true ]; then
        print_status "Setting up database with Docker..."
        
        # Start only database services
        docker-compose up -d postgres redis
        
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        sleep 10
        
        # Run migrations
        print_status "Running database migrations..."
        cd backend
        source venv/bin/activate
        alembic upgrade head
        print_success "Database migrations completed"
        
        # Seed database
        print_status "Seeding database with sample data..."
        python scripts/seed_data.py
        print_success "Database seeded with sample data"
        
        cd ..
    else
        print_warning "Docker not available. Please set up PostgreSQL and Redis manually."
        print_warning "Then run: cd backend && alembic upgrade head && python scripts/seed_data.py"
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Backend tests
    print_status "Running backend tests..."
    cd backend
    source venv/bin/activate
    
    if command_exists pytest; then
        pytest tests/ -v
        print_success "Backend tests completed"
    else
        print_warning "pytest not found, skipping backend tests"
    fi
    
    cd ..
    
    # Frontend tests
    print_status "Running frontend tests..."
    cd frontend
    
    npm test
    print_success "Frontend tests completed"
    
    cd ..
}

# Function to display final instructions
display_instructions() {
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo ""
    echo "1. 📝 Edit the .env file with your actual configuration:"
    echo "   - Database credentials"
    echo "   - API keys (OpenAI, Google Vision, Twilio)"
    echo "   - JWT secret key"
    echo ""
    echo "2. 🚀 Start the development servers:"
    echo ""
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_COMPOSE_AVAILABLE" = true ]; then
        echo "   Option A - Using Docker (Recommended):"
        echo "   docker-compose up"
        echo ""
    fi
    echo "   Option B - Manual startup:"
    echo "   # Terminal 1 - Backend"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   uvicorn app.main:app --reload"
    echo ""
    echo "   # Terminal 2 - Frontend"
    echo "   cd frontend"
    echo "   npm run dev"
    echo ""
    echo "3. 🌐 Access the application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "4. 🔑 Demo credentials:"
    echo "   - Admin: admin@example.com / admin123"
    echo "   - Student: student1@example.com / student123"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "🎓 Student Learning & Safety Platform Setup"
    echo "=========================================="
    echo -e "${NC}"
    
    check_requirements
    setup_environment
    setup_backend
    setup_frontend
    
    # Ask user if they want to set up database
    echo ""
    read -p "Do you want to set up the database now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_database
    else
        print_warning "Skipping database setup. You'll need to set it up manually later."
    fi
    
    # Ask user if they want to run tests
    echo ""
    read -p "Do you want to run tests now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    else
        print_warning "Skipping tests. You can run them later with: npm test"
    fi
    
    display_instructions
}

# Run main function
main "$@"