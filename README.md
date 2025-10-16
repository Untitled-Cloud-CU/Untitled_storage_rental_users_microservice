# Storage Rental - Users Service

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)

Microservice for managing user accounts, authentication, and user-related operations in the Storage Rental application.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [API Endpoints](#api-endpoints)
- [Setup Instructions](#setup-instructions)
- [Testing](#testing)
- [Sprint 1 Status](#sprint-1-status)
- [Project Structure](#project-structure)
- [Development Team](#development-team)

## ✨ Features

- User registration and profile management
- User authentication (login)
- User CRUD operations (Create, Read, Update, Delete)
- Retrieve user rental history
- Auto-generated OpenAPI documentation
- Input validation using Pydantic models
- RESTful API design

## 🛠 Technology Stack

- **FastAPI** - Modern, fast Python web framework
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - Lightning-fast ASGI server
- **Python 3.9+** - Programming language

## 🚀 API Endpoints

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/` | List all users (paginated) |
| GET | `/api/v1/users/{user_id}` | Get specific user by ID |
| POST | `/api/v1/users/` | Create new user |
| PUT | `/api/v1/users/{user_id}` | Update user information |
| DELETE | `/api/v1/users/{user_id}` | Delete user account |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/register` | Register new user account |
| POST | `/api/v1/users/login` | Authenticate user and return token |

### Rentals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{user_id}/rentals` | Get user's rental history |
| GET | `/api/v1/users/{user_id}/rentals/{rental_id}` | Get specific rental details |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/health` | Health check |

## 📦 Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/your-username/storage-rental-users-service.git
   cd storage-rental-users-service
```

2. **Create virtual environment**
```bash
   python3 -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Run the service**
```bash
   uvicorn app.main:app --reload --port 8000
```

5. **Access the API documentation**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing

You can test the endpoints using:

### Interactive Swagger UI
Navigate to http://localhost:8000/docs and use the built-in testing interface.

### cURL Commands
```bash
# Get all users
curl http://localhost:8000/api/v1/users/

# Get specific user
curl http://localhost:8000/api/v1/users/1

# Create new user
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@email.com",
    "password": "securepassword123",
    "phone": "555-0102"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.smith@email.com",
    "password": "password123"
  }'

# Health check
curl http://localhost:8000/health
```

### Postman
Import the OpenAPI specification from `/openapi.json` into Postman for comprehensive testing.

## 📊 Sprint 1 Status

**Current Implementation:** Basic structure with stubbed endpoints

### ✅ Completed
- All REST endpoints defined (GET, POST, PUT, DELETE)
- Pydantic models for data validation
- OpenAPI documentation auto-generated
- Returns "NOT IMPLEMENTED" stub responses
- CORS middleware configured
- Health check endpoint
- Comprehensive documentation

### 🚧 Coming in Sprint 2
- Actual business logic implementation
- Database integration (PostgreSQL/MySQL)
- Authentication with JWT tokens
- Password hashing (bcrypt)
- Input validation and error handling
- Unit and integration tests
- Docker containerization
- CI/CD pipeline

## 📁 Project Structure
```
storage-rental-users-service/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application setup
│   ├── models.py            # Pydantic data models
│   └── routers/
│       ├── __init__.py      # Router package initialization
│       └── users.py         # User endpoint implementations
├── tests/                   # Test files (coming in Sprint 2)
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 👥 Development Team

- **Sahasra** - Backend Developer
- **Molly** - Backend Developer

## 🔗 Related Services

This microservice is part of the larger Storage Rental Application:

- **Users Service** (this service) - User account management
- **Facilities Service** - Storage location and unit inventory
- **Orders Service** - Rental agreements and payment processing
- **Web Application** - User-facing frontend
- **Database** - Shared data persistence layer

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a student project for Columbia University's Cloud Computing course (W4153).

## 📞 Support

For questions or issues:
- Create an issue in this repository
- Contact the development team
- Check the project documentation

---

**Sprint 1 - September 2024**
