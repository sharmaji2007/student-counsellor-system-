#!/bin/bash

# 🚀 Student Learning & Safety Platform Deployment Script
# This script helps deploy the platform to various cloud providers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check deployment requirements
check_deployment_requirements() {
    print_status "Checking deployment requirements..."
    
    # Check Git
    if ! command_exists git; then
        print_error "Git is required for deployment"
        exit 1
    fi
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository. Please initialize git first."
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes. Consider committing them first."
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Deployment requirements check passed"
}

# Function to deploy to Vercel
deploy_to_vercel() {
    print_status "Deploying frontend to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command_exists vercel; then
        print_status "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    # Navigate to frontend directory
    cd frontend
    
    # Deploy to Vercel
    print_status "Deploying to Vercel..."
    vercel --prod
    
    print_success "Frontend deployed to Vercel successfully!"
    cd ..
}

# Function to deploy to Railway
deploy_to_railway() {
    print_status "Deploying backend to Railway..."
    
    # Check if Railway CLI is installed
    if ! command_exists railway; then
        print_status "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    # Login to Railway (if not already logged in)
    if ! railway whoami > /dev/null 2>&1; then
        print_status "Please login to Railway..."
        railway login
    fi
    
    # Deploy to Railway
    print_status "Deploying to Railway..."
    railway up
    
    print_success "Backend deployed to Railway successfully!"
}

# Function to deploy to Render
deploy_to_render() {
    print_status "Deploying to Render..."
    
    print_status "For Render deployment:"
    echo "1. Push your code to GitHub"
    echo "2. Connect your GitHub repository to Render"
    echo "3. Use the render.yaml configuration file"
    echo "4. Set environment variables in Render dashboard"
    
    # Push to GitHub
    read -p "Push to GitHub now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Deploy to Render" || true
        git push origin main
        print_success "Code pushed to GitHub"
    fi
    
    print_warning "Complete the deployment in Render dashboard"
}

# Function to setup environment variables
setup_environment_variables() {
    print_status "Setting up environment variables for deployment..."
    
    # Create production environment file
    if [ ! -f ".env.production" ]; then
        cp .env.example .env.production
        print_success "Created .env.production file"
        print_warning "Please edit .env.production with production values"
        
        # Open file for editing
        read -p "Open .env.production for editing? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env.production
        fi
    else
        print_warning ".env.production already exists"
    fi
}

# Function to run pre-deployment checks
run_pre_deployment_checks() {
    print_status "Running pre-deployment checks..."
    
    # Check if build passes
    print_status "Testing frontend build..."
    cd frontend
    npm run build
    print_success "Frontend build successful"
    cd ..
    
    # Check if backend tests pass
    print_status "Running backend tests..."
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    if command_exists pytest; then
        pytest tests/ -v
        print_success "Backend tests passed"
    else
        print_warning "pytest not found, skipping backend tests"
    fi
    cd ..
    
    # Check for security vulnerabilities
    print_status "Checking for security vulnerabilities..."
    cd frontend
    npm audit --audit-level=high
    cd ..
    
    print_success "Pre-deployment checks completed"
}

# Function to display deployment URLs
display_deployment_info() {
    print_success "🎉 Deployment completed!"
    echo ""
    echo -e "${BLUE}📋 Deployment Information:${NC}"
    echo ""
    echo "Frontend (Vercel):"
    echo "  - Production URL: https://your-app.vercel.app"
    echo "  - Dashboard: https://vercel.com/dashboard"
    echo ""
    echo "Backend (Railway/Render):"
    echo "  - API URL: https://your-backend.railway.app"
    echo "  - Dashboard: https://railway.app/dashboard"
    echo ""
    echo "📝 Post-deployment tasks:"
    echo "1. Update VITE_API_URL in Vercel environment variables"
    echo "2. Update CORS_ORIGINS in backend environment variables"
    echo "3. Test all functionality in production"
    echo "4. Set up monitoring and alerts"
    echo "5. Configure custom domain (optional)"
    echo ""
    echo -e "${GREEN}🚀 Your platform is now live!${NC}"
}

# Function to show help
show_help() {
    echo "Student Learning & Safety Platform Deployment Script"
    echo "=================================================="
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  vercel     Deploy frontend to Vercel"
    echo "  railway    Deploy backend to Railway"
    echo "  render     Deploy to Render"
    echo "  full       Full deployment (Vercel + Railway)"
    echo "  check      Run pre-deployment checks only"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 full      # Deploy both frontend and backend"
    echo "  $0 vercel    # Deploy only frontend to Vercel"
    echo "  $0 railway   # Deploy only backend to Railway"
    echo "  $0 check     # Run checks without deploying"
}

# Main function
main() {
    case "${1:-help}" in
        "vercel")
            check_deployment_requirements
            setup_environment_variables
            run_pre_deployment_checks
            deploy_to_vercel
            ;;
        "railway")
            check_deployment_requirements
            setup_environment_variables
            run_pre_deployment_checks
            deploy_to_railway
            ;;
        "render")
            check_deployment_requirements
            setup_environment_variables
            run_pre_deployment_checks
            deploy_to_render
            ;;
        "full")
            check_deployment_requirements
            setup_environment_variables
            run_pre_deployment_checks
            deploy_to_vercel
            deploy_to_railway
            display_deployment_info
            ;;
        "check")
            check_deployment_requirements
            run_pre_deployment_checks
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Header
echo -e "${BLUE}"
echo "🚀 Student Learning & Safety Platform Deployment"
echo "=============================================="
echo -e "${NC}"

# Run main function with arguments
main "$@"