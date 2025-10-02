import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "student"
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "student"

@pytest.mark.asyncio
async def test_login_user():
    """Test user login"""
    # First register a user
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "password": "testpass123",
            "full_name": "Login User",
            "role": "student"
        })
        
        # Then login
        response = await ac.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "testpass123"
        })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpass"
        })
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]