# Quick Start Guide

Get the Storage Rental Users Service up and running in 5 minutes!

## Option 1: Docker (Easiest)

```bash
# 1. Start everything with Docker Compose
docker-compose up -d

# 2. Check if it's running
curl http://localhost:8000/health

# 3. Visit the API docs
open http://localhost:8000/docs
```

## Option 2: Local Development

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Run the service
uvicorn app.main:app --reload

# 5. Visit http://localhost:8000/docs
```

## First API Calls

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "phone": "555-0100"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### 3. Get User Info (with token)
```bash
curl http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Common Commands

```bash
# Run with Make
make install    # Install dependencies
make run        # Run the service
make test       # Run tests
make docker-up  # Start with Docker

# Run tests
pytest

# Clean up
make clean
```

Happy coding! 🚀
