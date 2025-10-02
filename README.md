# 🎓 Student Learning & Safety Platform

A comprehensive AI-powered platform for educational institutions featuring student management, learning assistance, and safety monitoring with real-time risk assessment.

[![Deploy Frontend](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/student-platform)
[![Deploy Backend](https://railway.app/button.svg)](https://railway.app/new/template/student-platform)

## ✨ Features

- 🔐 **Role-Based Authentication** - Student, Teacher, Mentor, Counselor, Admin access levels
- 📚 **Smart Assignment System** - Photo upload with OCR processing and AI quiz generation
- 🛡️ **Safety Monitoring** - Real-time chat analysis with SOS alert system
- 📊 **Risk Assessment** - Multi-factor student risk scoring and intervention alerts
- 🤖 **AI Learning Tools** - OCR text extraction and automatic quiz generation
- 💬 **Secure Communication** - Private chat with safety keyword detection
- 📱 **Responsive Design** - Mobile-first, accessible interface

## 🚀 Tech Stack

### Frontend
- **React 18** + TypeScript + Vite
- **Tailwind CSS** for styling
- **React Query** for state management
- **React Router** for navigation
- **Zustand** for global state
- **React Hook Form** + Zod validation

### Backend
- **FastAPI** + Python 3.11+
- **SQLAlchemy** (async) + PostgreSQL
- **Redis** + RQ for background jobs
- **JWT** authentication
- **OpenAI** + Google Vision APIs
- **Twilio** for notifications

### Infrastructure
- **Docker** + Docker Compose
- **Vercel** (Frontend deployment)
- **Railway/Render** (Backend deployment)
- **MinIO/S3** for file storage
- **GitHub Actions** CI/CD

## 🏃‍♂️ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/student-platform.git
cd student-platform
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env
```

### 3. Local Development with Docker
```bash
# Start all services
docker-compose up --build

# In another terminal, run migrations and seed data
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed_data.py
```

### 4. Access Application
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs
- 💾 **MinIO Console**: http://localhost:9001

## 🔧 Manual Development Setup

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/student_platform"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="your-secret-key"

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed_data.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

## 🚀 Production Deployment

### Deploy Frontend to Vercel

1. **Push to GitHub**:
```bash
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/student-platform.git
git push -u origin main
```

2. **Deploy to Vercel**:
   - Visit [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Set build settings:
     - **Framework**: Vite
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
   - Add environment variables:
     - `VITE_API_URL`: Your backend URL

3. **Environment Variables for Vercel**:
```bash
VITE_API_URL=https://your-backend-url.railway.app
```

### Deploy Backend to Railway

1. **Connect to Railway**:
   - Visit [railway.app](https://railway.app)
   - Connect your GitHub repository
   - Select the backend folder

2. **Environment Variables for Railway**:
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
JWT_SECRET_KEY=your-super-secret-key
OPENAI_API_KEY=your-openai-key
GOOGLE_VISION_API_KEY=your-google-vision-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
ENVIRONMENT=production
```

3. **Railway Configuration**:
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Build Command**: `pip install -r requirements.txt`

### Alternative: Deploy Backend to Render

1. **Create Render Account**: Visit [render.com](https://render.com)
2. **Create Web Service**: Connect your GitHub repo
3. **Configuration**:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🧪 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Teacher | teacher@example.com | teacher123 |
| Counselor | counselor@example.com | counselor123 |
| Student | student1@example.com | student123 |

## 🎯 Demo Flow

1. **Login** as admin to explore all features
2. **Create Assignment** (Teacher role) and upload handwritten notes
3. **OCR Processing** - Watch AI extract text and generate quiz questions
4. **Risk Monitoring** - Check student dashboard for risk assessment
5. **Safety Chat** - Test private chat with safety keyword detection
6. **Admin Panel** - Manage users and monitor SOS incidents

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

### E2E Testing
```bash
# Run full application
docker-compose up -d

# Run tests against running application
npm run test:e2e
```

## 📁 Project Structure

```
student-platform/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── stores/         # Zustand state management
│   │   ├── lib/            # API client and utilities
│   │   └── test/           # Test files
│   ├── public/             # Static assets
│   └── package.json
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── workers/        # Background jobs
│   ├── alembic/            # Database migrations
│   ├── scripts/            # Utility scripts
│   ├── tests/              # Test files
│   └── requirements.txt
├── .github/workflows/       # CI/CD pipelines
├── docker-compose.yml       # Local development setup
├── .env.example            # Environment template
└── README.md
```

## 🔒 Security Features

- 🔐 JWT authentication with refresh tokens
- 🛡️ Role-based access control (RBAC)
- 🔍 Input validation and sanitization
- ⚡ Rate limiting on sensitive endpoints
- 🗑️ Automatic data retention policies
- 🚨 Real-time safety monitoring
- 📝 Comprehensive audit logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 **Email**: support@studentplatform.com
- 💬 **Discord**: [Join our community](https://discord.gg/studentplatform)
- 📖 **Documentation**: [docs.studentplatform.com](https://docs.studentplatform.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/student-platform/issues)

## 🙏 Acknowledgments

- OpenAI for GPT integration
- Google Cloud Vision for OCR capabilities
- Twilio for communication services
- The open-source community for amazing tools

---

**⭐ Star this repository if you find it helpful!**