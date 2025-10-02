# 🚀 Deployment Guide

This guide will walk you through deploying the Student Learning & Safety Platform to production using Vercel (frontend) and Railway (backend).

## 📋 Prerequisites

- GitHub account
- Vercel account (free tier available)
- Railway account (free tier available)
- Domain name (optional)

## 🔧 Environment Variables

### Frontend (.env.local)
```bash
VITE_API_URL=https://your-backend-url.railway.app
```

### Backend (Production)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Redis
REDIS_URL=redis://host:port/0

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Services
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Google Vision API
GOOGLE_VISION_API_KEY=your-google-vision-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Twilio (SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Storage (Production)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-s3-bucket-name

# Application
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]

# Safety Configuration
COUNSELOR_PHONE=+1234567890
COUNSELOR_EMAIL=counselor@school.edu
```

## 🚀 Step-by-Step Deployment

### 1. Prepare Repository

```bash
# Clone your repository
git clone https://github.com/yourusername/student-platform.git
cd student-platform

# Ensure all files are committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Deploy Backend to Railway

1. **Sign up for Railway**: Visit [railway.app](https://railway.app)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select "Deploy Now"

3. **Configure Build Settings**:
   - Railway will auto-detect Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Database**:
   - In your Railway project, click "New"
   - Select "Database" → "PostgreSQL"
   - Railway will provide a `DATABASE_URL`

5. **Add Redis**:
   - Click "New" → "Database" → "Redis"
   - Railway will provide a `REDIS_URL`

6. **Set Environment Variables**:
   ```bash
   # In Railway dashboard, go to Variables tab
   DATABASE_URL=postgresql://... (from Railway PostgreSQL)
   REDIS_URL=redis://... (from Railway Redis)
   JWT_SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-key
   ENVIRONMENT=production
   # ... add all other variables
   ```

7. **Deploy**:
   - Railway will automatically deploy
   - Note your backend URL: `https://your-app.railway.app`

### 3. Deploy Frontend to Vercel

1. **Sign up for Vercel**: Visit [vercel.com](https://vercel.com)

2. **Import Project**:
   - Click "New Project"
   - Import your GitHub repository
   - Select the repository

3. **Configure Build Settings**:
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Set Environment Variables**:
   ```bash
   VITE_API_URL=https://your-backend-url.railway.app
   ```

5. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy your frontend
   - Note your frontend URL: `https://your-app.vercel.app`

### 4. Configure Custom Domain (Optional)

#### For Vercel (Frontend):
1. Go to your project settings
2. Click "Domains"
3. Add your custom domain
4. Configure DNS records as instructed

#### For Railway (Backend):
1. Go to your service settings
2. Click "Networking"
3. Add custom domain
4. Configure DNS records

### 5. Set up CI/CD (GitHub Actions)

Add these secrets to your GitHub repository:

1. **Go to Repository Settings** → Secrets and Variables → Actions

2. **Add Repository Secrets**:
   ```bash
   # Vercel
   VERCEL_TOKEN=your-vercel-token
   VERCEL_ORG_ID=your-vercel-org-id
   VERCEL_PROJECT_ID=your-vercel-project-id
   
   # Railway
   RAILWAY_TOKEN=your-railway-token
   
   # Docker Hub (optional)
   DOCKER_USERNAME=your-docker-username
   DOCKER_PASSWORD=your-docker-password
   ```

3. **Get Vercel Tokens**:
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login and get tokens
   vercel login
   vercel link
   
   # Get org and project IDs from .vercel/project.json
   ```

4. **Get Railway Token**:
   - Go to Railway dashboard
   - Account Settings → Tokens
   - Create new token

## 🔍 Verification Steps

### 1. Test Backend Deployment
```bash
# Check health endpoint
curl https://your-backend-url.railway.app/health

# Check API documentation
open https://your-backend-url.railway.app/docs
```

### 2. Test Frontend Deployment
```bash
# Visit your frontend
open https://your-app.vercel.app

# Test login with demo credentials
# Email: admin@example.com
# Password: admin123
```

### 3. Test Full Integration
1. Login to the application
2. Upload an assignment image
3. Verify OCR processing works
4. Test chat functionality
5. Check risk dashboard

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues:
```bash
# Check Railway logs
railway logs

# Database connection issues
# Ensure DATABASE_URL is correctly set
# Check if database is running

# Redis connection issues
# Ensure REDIS_URL is correctly set
# Check if Redis service is running
```

#### Frontend Issues:
```bash
# Check Vercel build logs
# Ensure VITE_API_URL points to correct backend

# CORS issues
# Add your frontend domain to CORS_ORIGINS in backend
```

#### Environment Variables:
```bash
# Backend not starting
# Check all required environment variables are set
# Verify JWT_SECRET_KEY is at least 32 characters

# API calls failing
# Verify VITE_API_URL in frontend matches backend URL
# Check network connectivity between services
```

### Performance Optimization

#### Backend:
```bash
# Enable database connection pooling
# Configure Redis for caching
# Set up CDN for file uploads
# Enable gzip compression
```

#### Frontend:
```bash
# Enable Vercel Analytics
# Configure caching headers
# Optimize images and assets
# Enable service worker for offline support
```

## 📊 Monitoring & Maintenance

### 1. Set up Monitoring
- **Sentry**: Error tracking and performance monitoring
- **Railway Metrics**: Database and service monitoring
- **Vercel Analytics**: Frontend performance and usage

### 2. Regular Maintenance
```bash
# Update dependencies monthly
npm audit fix  # Frontend
pip-audit      # Backend

# Monitor database performance
# Clean up expired chat messages
# Review and rotate API keys quarterly
```

### 3. Backup Strategy
```bash
# Database backups (Railway provides automatic backups)
# File storage backups (S3 versioning)
# Environment variables backup (secure storage)
```

## 🔒 Security Checklist

- [ ] All API keys stored as environment variables
- [ ] JWT secret key is strong (32+ characters)
- [ ] CORS origins properly configured
- [ ] Rate limiting enabled on sensitive endpoints
- [ ] Database credentials rotated regularly
- [ ] SSL/TLS certificates configured
- [ ] Security headers configured
- [ ] Input validation on all endpoints
- [ ] File upload restrictions in place
- [ ] Audit logging enabled

## 📞 Support

If you encounter issues during deployment:

1. Check the [troubleshooting section](#troubleshooting)
2. Review service logs (Railway/Vercel dashboards)
3. Verify all environment variables are set correctly
4. Test locally with production environment variables
5. Create an issue in the GitHub repository

## 🎉 Success!

Once deployed successfully, your Student Learning & Safety Platform will be:

- ✅ **Frontend**: Live on Vercel with global CDN
- ✅ **Backend**: Running on Railway with auto-scaling
- ✅ **Database**: PostgreSQL with automatic backups
- ✅ **CI/CD**: Automated deployments on every push
- ✅ **Monitoring**: Error tracking and performance monitoring
- ✅ **Security**: Production-grade security measures

Your platform is now ready to serve students and educators worldwide! 🌍