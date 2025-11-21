# Storage Rental - Users Service

Microservice for managing user accounts, authentication, and user-related operations in the Storage Rental application.


## ✨ Features

- User registration and profile management
- User authentication (JWT-based login)
- User CRUD operations (Create, Read, Update, Delete)
- Secure password hashing with bcrypt
- Authorization (users can only modify their own data)
- Retrieve user rental history
- Auto-generated OpenAPI documentation
- Input validation using Pydantic models
- PostgreSQL database integration
- Docker containerization
- Comprehensive automated testing
- RESTful API design

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

- Docker and Docker Compose (recommended)
- Python 3.11 or higher (for local development)
- Git

### Quick Start with Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/Untitled-Cloud-CU/Untitled_storage_rental_users_microservice.git
cd Untitled_storage_rental_users_microservice
```

2. **Start the services**
```bash
docker compose up -d
```

3. **Verify services are running**
```bash
docker compose ps
```

4. **Access the API**
   - **API**: http://localhost:8000
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

### Local Development Setup (Without Docker)

1. **Clone the repository**
```bash
git clone https://github.com/Untitled-Cloud-CU/Untitled_storage_rental_users_microservice.git
cd Untitled_storage_rental_users_microservice
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

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run the service**
```bash
uvicorn app.main:app --reload --port 8000
```

6. **Access the API documentation**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing

### Run Automated Tests
```bash
# Quick test suite (8 core tests)
./test_api.sh

# Complete test suite (20 tests)
./test_complete.sh

# pytest tests
pytest -v

# With coverage
pytest --cov=app --cov-report=html
```

**Test Results:** 20/20 passing (100% pass rate)

### Interactive Testing with Swagger UI

Navigate to http://localhost:8000/docs and use the built-in testing interface.

### Example cURL Commands
```bash
# Health check
curl http://localhost:8000/health

# Register a new user
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@email.com",
    "password": "SecurePass123",
    "phone": "555-0102"
  }'

# Login and get JWT token
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.doe@email.com",
    "password": "SecurePass123"
  }'

# Get all users
curl http://localhost:8000/api/v1/users/

# Get specific user
curl http://localhost:8000/api/v1/users/1

# Update user (requires authentication token)
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "phone": "555-9999"
  }'

# Delete user (requires authentication token)
curl -X DELETE http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Postman

Import the OpenAPI specification from `/openapi.json` into Postman for comprehensive testing.

## 🔐 Authentication

This service uses JWT (JSON Web Tokens) for authentication.

### How to Authenticate:

1. **Register** a new user at `/api/v1/users/register`
2. **Login** at `/api/v1/users/login` to receive a JWT token
3. **Use the token** in the `Authorization` header for protected endpoints:
```
   Authorization: Bearer <your_jwt_token>
```

### Token Details:
- **Algorithm:** HS256
- **Expiration:** 30 minutes
- **Protected Endpoints:** PUT, DELETE operations require valid token
- **Authorization:** Users can only modify their own accounts

## 🐳 Docker Commands
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f users-service

# Restart service
docker compose restart users-service

# Rebuild containers
docker compose build --no-cache

# Remove all (including database volumes)
docker compose down -v

# Access PostgreSQL database
docker compose exec db psql -U storage_user -d storage_rental_users
```

## 📊 Project Status

### ✅ Sprint 1 - COMPLETE
- [x] All REST endpoints defined (GET, POST, PUT, DELETE)
- [x] Pydantic models for data validation
- [x] OpenAPI documentation auto-generated
- [x] CORS middleware configured
- [x] Health check endpoint
- [x] Comprehensive documentation

### ✅ Sprint 2 - COMPLETE
- [x] **Full business logic implementation**
- [x] **PostgreSQL database integration with SQLAlchemy**
- [x] **JWT token authentication**
- [x] **bcrypt password hashing**
- [x] **Comprehensive input validation and error handling**
- [x] **Authorization (users can only modify own data)**
- [x] **Automated testing suite (20 tests, 100% pass rate)**
- [x] **Docker containerization**
- [x] **CI/CD pipeline structure**

### 🚧 PLANNED
- [ ] Email verification
- [ ] Password reset functionality
- [ ] User roles and permissions (admin, user)
- [ ] Profile picture upload
- [ ] Two-factor authentication (2FA)
- [ ] Rate limiting
- [ ] Redis caching

## 📁 Project Structure
```
Untitled_storage_rental_users_microservice/
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # CI/CD pipeline configuration
├── app/
│   ├── __init__.py                # Package initialization
│   ├── main.py                    # FastAPI application setup
│   ├── config.py                  # Configuration settings
│   ├── database.py                # Database connection
│   ├── db_models.py               # SQLAlchemy database models
│   ├── schemas.py                 # Pydantic request/response models
│   ├── security.py                # JWT and password utilities
│   ├── dependencies.py            # Shared dependencies
│   ├── crud/
│   │   ├── __init__.py
│   │   └── users.py               # Database operations (CRUD)
│   └── routers/
│       ├── __init__.py
│       └── users.py               # User endpoint implementations
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures
│   └── test_users.py              # Unit tests
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── .dockerignore                  # Docker ignore rules
├── Dockerfile                     # Container configuration
├── docker-compose.yml             # Multi-container orchestration
├── requirements.txt               # Python dependencies
├── pytest.ini                     # pytest configuration
├── Makefile                       # Command shortcuts
├── test_api.sh                    # Quick API testing script
├── test_complete.sh               # Complete test suite (20 tests)
├── QUICKSTART.md                  # Quick start guide
└── README.md                      # This file
```

## 🛠️ Technology Stack

- **Framework:** FastAPI 0.104.1
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt 4.0.1
- **Validation:** Pydantic 2.5
- **Testing:** pytest
- **Containerization:** Docker & Docker Compose
- **Documentation:** OpenAPI/Swagger (auto-generated)

## 🔒 Security Features

### Password Security
- Passwords hashed with bcrypt (cost factor: 12)
- Never stored in plain text
- Minimum 8 characters required
- Must contain letters and digits
- Salted hashes for each password

### Authentication & Authorization
- JWT tokens with HS256 algorithm
- 30-minute token expiration
- Token validation on protected endpoints
- Users can only modify their own data
- 403 Forbidden for unauthorized access

### Input Validation
- Email format validation
- Password strength requirements
- Phone number format validation
- Duplicate email prevention
- SQL injection prevention (SQLAlchemy ORM)

## 📈 Performance

- Response time: < 100ms for most endpoints
- Database queries optimized with indexes
- Connection pooling configured
- Health checks for monitoring

## 🗄️ Database

### Schema

**Users Table:**
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    status userstatus NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);
```

**User Status:** `ACTIVE`, `INACTIVE`, `SUSPENDED`

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in docker-compose.yml or stop conflicting service
docker compose down
```

**Database connection failed:**
```bash
# Check if database is running
docker compose ps
# Restart database
docker compose restart db
```

**bcrypt errors:**
- Ensure bcrypt==4.0.1 is installed
- Rebuild Docker containers if needed

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://storage_user:storage_pass@db:5432/storage_rental_users` |
| `SECRET_KEY` | JWT secret key | Auto-generated (change in production!) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |

## 👥 Team Members

- **Sahasra** - Backend Development
- **Molly** - Backend Development & Testing

## 🔗 Related Services

This microservice is part of the larger Storage Rental Application:

- **Users Service** (this service) - User account management
- **Facilities Service** (coming soon) - Storage location and unit inventory
- **Orders Service** (coming soon) - Rental agreements and payment processing
- **Web Application** (coming soon) - User-facing frontend




