# 🤝 Contributing to Student Learning & Safety Platform

Thank you for your interest in contributing to the Student Learning & Safety Platform! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Standards](#development-standards)

## 📜 Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome contributors from all backgrounds
- **Be collaborative**: Work together to improve the platform
- **Be constructive**: Provide helpful feedback and suggestions
- **Be professional**: Maintain a professional tone in all interactions

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+ and pip
- **Docker** and Docker Compose
- **Git** for version control
- **PostgreSQL** (or use Docker)
- **Redis** (or use Docker)

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/student-platform.git
   cd student-platform
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/originalowner/student-platform.git
   ```

## 🛠️ Development Setup

### Quick Setup with Docker
```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up --build

# Run migrations and seed data
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed_data.py
```

### Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed_data.py

# Start server
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📚 **Documentation improvements**
- 🧪 **Tests**
- 🎨 **UI/UX improvements**
- 🔧 **Performance optimizations**
- 🌐 **Translations**

### Before You Start

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** for new features or major changes
3. **Discuss your approach** in the issue comments
4. **Keep changes focused** - one feature/fix per PR

### Branch Naming Convention

Use descriptive branch names:
```bash
# Feature branches
feature/assignment-upload-ui
feature/risk-scoring-algorithm

# Bug fix branches
fix/chat-message-validation
fix/login-redirect-issue

# Documentation branches
docs/deployment-guide
docs/api-documentation
```

## 🔄 Pull Request Process

### 1. Prepare Your Changes

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make your changes
# ... code, test, commit ...

# Keep your branch updated
git fetch upstream
git rebase upstream/main
```

### 2. Testing Requirements

Before submitting a PR, ensure:

#### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run lint
npm run build
```

#### Integration Tests
```bash
# Start services
docker-compose up -d

# Run end-to-end tests
npm run test:e2e
```

### 3. Commit Guidelines

Use conventional commit messages:
```bash
# Format: type(scope): description

feat(auth): add Google OAuth integration
fix(chat): resolve message ordering issue
docs(readme): update installation instructions
test(api): add tests for risk scoring
style(ui): improve mobile responsiveness
refactor(db): optimize query performance
```

### 4. Submit Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR** on GitHub with:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes
   - Test results
   - Breaking changes (if any)

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement

   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests
   - [ ] Manual testing completed

   ## Screenshots (if applicable)
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes
   ```

## 🐛 Issue Reporting

### Bug Reports

Use the bug report template:
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Version: [e.g. 1.0.0]

**Additional Context**
Any other relevant information
```

### Feature Requests

Use the feature request template:
```markdown
**Feature Description**
Clear description of the feature

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should this work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Mockups, examples, etc.
```

## 🎯 Development Standards

### Code Style

#### Python (Backend)
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Maximum line length: 88 characters
- Use type hints where possible

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

#### TypeScript/React (Frontend)
- Follow **ESLint** configuration
- Use **Prettier** for formatting
- Use **TypeScript** strict mode
- Follow React best practices

```bash
# Format and lint
npm run lint
npm run format
```

### Testing Standards

#### Backend Testing
- **Unit tests** for business logic
- **Integration tests** for API endpoints
- **Minimum 80% code coverage**
- Use **pytest** fixtures for setup
- Mock external services

```python
# Example test structure
def test_create_user_success(db_session):
    """Test successful user creation."""
    user_data = {"email": "test@example.com", "password": "password123"}
    user = create_user(db_session, user_data)
    assert user.email == "test@example.com"
```

#### Frontend Testing
- **Unit tests** for components
- **Integration tests** for user flows
- **Accessibility tests**
- Use **React Testing Library**

```typescript
// Example component test
test('renders login form', () => {
  render(<LoginForm />)
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
})
```

### Documentation Standards

- **Code comments** for complex logic
- **API documentation** with OpenAPI/Swagger
- **README updates** for new features
- **Inline documentation** for functions
- **Architecture decisions** recorded

### Security Guidelines

- **Never commit secrets** or API keys
- **Validate all inputs** on backend
- **Sanitize user data** before storage
- **Use parameterized queries** for database
- **Implement rate limiting** for APIs
- **Follow OWASP guidelines**

### Performance Guidelines

- **Optimize database queries**
- **Use caching** where appropriate
- **Minimize bundle size** (frontend)
- **Lazy load components** when possible
- **Profile and measure** performance

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page
- **Special mentions** in project updates

## 📞 Getting Help

If you need help:

1. **Check documentation** first
2. **Search existing issues**
3. **Ask in discussions** for general questions
4. **Create an issue** for specific problems
5. **Join our Discord** for real-time chat

## 🎉 Thank You!

Every contribution, no matter how small, helps make this platform better for students and educators worldwide. Thank you for being part of our community!

---

**Happy Contributing! 🚀**