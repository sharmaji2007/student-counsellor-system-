# 🚀 Student Learning & Safety Platform Setup Script (Windows PowerShell)
# This script sets up the development environment for the platform

param(
    [switch]$SkipDatabase,
    [switch]$SkipTests,
    [switch]$Help
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-Requirements {
    Write-Status "Checking system requirements..."
    
    # Check Node.js
    if (Test-Command "node") {
        $nodeVersion = (node --version).Substring(1)
        Write-Success "Node.js found: v$nodeVersion"
        
        # Check if version is >= 18
        if ([version]$nodeVersion -ge [version]"18.0.0") {
            Write-Success "Node.js version is compatible"
        }
        else {
            Write-Error "Node.js version must be >= 18.0.0"
            exit 1
        }
    }
    else {
        Write-Error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    }
    
    # Check npm
    if (Test-Command "npm") {
        $npmVersion = npm --version
        Write-Success "npm found: v$npmVersion"
    }
    else {
        Write-Error "npm is not installed"
        exit 1
    }
    
    # Check Python
    if (Test-Command "python") {
        $pythonVersion = (python --version).Split(" ")[1]
        Write-Success "Python found: v$pythonVersion"
        
        if ([version]$pythonVersion -ge [version]"3.11.0") {
            Write-Success "Python version is compatible"
        }
        else {
            Write-Warning "Python version should be >= 3.11.0 for best compatibility"
        }
    }
    else {
        Write-Error "Python is not installed. Please install Python 3.11+ from https://python.org/"
        exit 1
    }
    
    # Check pip
    if (Test-Command "pip") {
        $pipVersion = (pip --version).Split(" ")[1]
        Write-Success "pip found: v$pipVersion"
    }
    else {
        Write-Error "pip is not installed"
        exit 1
    }
    
    # Check Git
    if (Test-Command "git") {
        $gitVersion = (git --version).Split(" ")[2]
        Write-Success "Git found: v$gitVersion"
    }
    else {
        Write-Error "Git is not installed. Please install Git from https://git-scm.com/"
        exit 1
    }
    
    # Check Docker (optional)
    if (Test-Command "docker") {
        $dockerVersion = (docker --version).Split(" ")[2].TrimEnd(",")
        Write-Success "Docker found: v$dockerVersion"
        $script:DockerAvailable = $true
    }
    else {
        Write-Warning "Docker is not installed. You can still run the project manually."
        $script:DockerAvailable = $false
    }
    
    # Check Docker Compose (optional)
    if (Test-Command "docker-compose" -or (docker compose version 2>$null)) {
        Write-Success "Docker Compose is available"
        $script:DockerComposeAvailable = $true
    }
    else {
        Write-Warning "Docker Compose is not available"
        $script:DockerComposeAvailable = $false
    }
}

function Setup-Environment {
    Write-Status "Setting up environment configuration..."
    
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Success "Created .env file from .env.example"
            Write-Warning "Please edit .env file with your actual configuration values"
        }
        else {
            Write-Error ".env.example file not found"
            exit 1
        }
    }
    else {
        Write-Warning ".env file already exists, skipping creation"
    }
}

function Setup-Backend {
    Write-Status "Setting up backend..."
    
    Set-Location "backend"
    
    # Create virtual environment
    if (-not (Test-Path "venv")) {
        Write-Status "Creating Python virtual environment..."
        python -m venv venv
        Write-Success "Virtual environment created"
    }
    else {
        Write-Warning "Virtual environment already exists"
    }
    
    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & ".\venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Status "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install dependencies
    Write-Status "Installing Python dependencies..."
    pip install -r requirements.txt
    Write-Success "Backend dependencies installed"
    
    Set-Location ".."
}

function Setup-Frontend {
    Write-Status "Setting up frontend..."
    
    Set-Location "frontend"
    
    # Install dependencies
    Write-Status "Installing Node.js dependencies..."
    npm install
    Write-Success "Frontend dependencies installed"
    
    # Create frontend environment file
    if (-not (Test-Path ".env.local")) {
        "VITE_API_URL=http://localhost:8000" | Out-File -FilePath ".env.local" -Encoding UTF8
        Write-Success "Created frontend .env.local file"
    }
    else {
        Write-Warning "Frontend .env.local file already exists"
    }
    
    Set-Location ".."
}

function Setup-Database {
    if ($script:DockerAvailable -and $script:DockerComposeAvailable) {
        Write-Status "Setting up database with Docker..."
        
        # Start only database services
        docker-compose up -d postgres redis
        
        # Wait for database to be ready
        Write-Status "Waiting for database to be ready..."
        Start-Sleep -Seconds 10
        
        # Run migrations
        Write-Status "Running database migrations..."
        Set-Location "backend"
        & ".\venv\Scripts\Activate.ps1"
        alembic upgrade head
        Write-Success "Database migrations completed"
        
        # Seed database
        Write-Status "Seeding database with sample data..."
        python scripts/seed_data.py
        Write-Success "Database seeded with sample data"
        
        Set-Location ".."
    }
    else {
        Write-Warning "Docker not available. Please set up PostgreSQL and Redis manually."
        Write-Warning "Then run: cd backend && .\venv\Scripts\Activate.ps1 && alembic upgrade head && python scripts/seed_data.py"
    }
}

function Run-Tests {
    Write-Status "Running tests..."
    
    # Backend tests
    Write-Status "Running backend tests..."
    Set-Location "backend"
    & ".\venv\Scripts\Activate.ps1"
    
    if (Test-Command "pytest") {
        pytest tests/ -v
        Write-Success "Backend tests completed"
    }
    else {
        Write-Warning "pytest not found, skipping backend tests"
    }
    
    Set-Location ".."
    
    # Frontend tests
    Write-Status "Running frontend tests..."
    Set-Location "frontend"
    
    npm test
    Write-Success "Frontend tests completed"
    
    Set-Location ".."
}

function Show-Instructions {
    Write-Success "🎉 Setup completed successfully!"
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "1. 📝 Edit the .env file with your actual configuration:"
    Write-Host "   - Database credentials"
    Write-Host "   - API keys (OpenAI, Google Vision, Twilio)"
    Write-Host "   - JWT secret key"
    Write-Host ""
    Write-Host "2. 🚀 Start the development servers:"
    Write-Host ""
    
    if ($script:DockerAvailable -and $script:DockerComposeAvailable) {
        Write-Host "   Option A - Using Docker (Recommended):"
        Write-Host "   docker-compose up"
        Write-Host ""
    }
    
    Write-Host "   Option B - Manual startup:"
    Write-Host "   # Terminal 1 - Backend"
    Write-Host "   cd backend"
    Write-Host "   .\venv\Scripts\Activate.ps1"
    Write-Host "   uvicorn app.main:app --reload"
    Write-Host ""
    Write-Host "   # Terminal 2 - Frontend"
    Write-Host "   cd frontend"
    Write-Host "   npm run dev"
    Write-Host ""
    Write-Host "3. 🌐 Access the application:"
    Write-Host "   - Frontend: http://localhost:3000"
    Write-Host "   - Backend API: http://localhost:8000"
    Write-Host "   - API Docs: http://localhost:8000/docs"
    Write-Host ""
    Write-Host "4. 🔑 Demo credentials:"
    Write-Host "   - Admin: admin@example.com / admin123"
    Write-Host "   - Student: student1@example.com / student123"
    Write-Host ""
    Write-Host "Happy coding! 🚀" -ForegroundColor $Green
}

function Show-Help {
    Write-Host "Student Learning & Safety Platform Setup Script" -ForegroundColor $Blue
    Write-Host "=============================================="
    Write-Host ""
    Write-Host "Usage: .\scripts\setup.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SkipDatabase    Skip database setup"
    Write-Host "  -SkipTests       Skip running tests"
    Write-Host "  -Help            Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\setup.ps1                    # Full setup"
    Write-Host "  .\scripts\setup.ps1 -SkipDatabase      # Skip database setup"
    Write-Host "  .\scripts\setup.ps1 -SkipTests         # Skip tests"
}

# Main execution
function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Write-Host "🎓 Student Learning & Safety Platform Setup" -ForegroundColor $Blue
    Write-Host "==========================================="
    Write-Host ""
    
    Test-Requirements
    Setup-Environment
    Setup-Backend
    Setup-Frontend
    
    if (-not $SkipDatabase) {
        $response = Read-Host "Do you want to set up the database now? (y/n)"
        if ($response -eq "y" -or $response -eq "Y") {
            Setup-Database
        }
        else {
            Write-Warning "Skipping database setup. You'll need to set it up manually later."
        }
    }
    
    if (-not $SkipTests) {
        $response = Read-Host "Do you want to run tests now? (y/n)"
        if ($response -eq "y" -or $response -eq "Y") {
            Run-Tests
        }
        else {
            Write-Warning "Skipping tests. You can run them later with: npm test"
        }
    }
    
    Show-Instructions
}

# Initialize variables
$script:DockerAvailable = $false
$script:DockerComposeAvailable = $false

# Run main function
Main