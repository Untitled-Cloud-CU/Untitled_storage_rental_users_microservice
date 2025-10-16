"""
Main application entry point
FastAPI application configuration and setup
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users

# Create FastAPI application
app = FastAPI(
    title="Storage Rental - Users Service API",
    description="""
    Microservice for managing user accounts and authentication in the Storage Rental system.
    
    **Features:**
    - User registration and profile management
    - User authentication and login  
    - CRUD operations for user accounts
    - Retrieve user rental history
    - Auto-generated OpenAPI documentation
    
    **Sprint 1 Status:** This is a Sprint 1 implementation with stubbed endpoints. All endpoints return "NOT IMPLEMENTED" responses.
    """,
    version="1.0.0",
    contact={
        "name": "Sahasra + Molly",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - Service information
    """
    return {
        "service": "Users Service",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "users": "/api/v1/users",
            "register": "/api/v1/users/register",
            "login": "/api/v1/users/login"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    Returns service health status
    """
    return {
        "status": "healthy",
        "service": "users-service",
        "version": "1.0.0"
    }

