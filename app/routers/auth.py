"""
Auth endpoints
Handles Google OAuth → JWT for the Users microservice
"""

from datetime import datetime, timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from ..database import SessionLocal
from ..models import User as UserSchema

# 🔴 IMPORTANT:
# This is your SQLAlchemy *DB* model for users.
# If your project uses a different module/name for it,
# change this import AND add the same import at the top of user.py.
try:
    from ..db_models import UserDB # <-- adjust if needed
except ImportError:
    # Fallback name in case you used a different file
    # e.g. from ..models_db import User as UserDB
    raise


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)

# --------------------------------------------------------------------
# Shared DB dependency (same pattern as in user.py)
# --------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBearer()

# --------------------------------------------------------------------
# Config – these should be set as env vars in Cloud Run
# --------------------------------------------------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "257248974057-dot98i5phvsc84ckf3paksk1m6l01e1t.apps.googleusercontent.com")

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


# --------------------------------------------------------------------
# Request / Response Models
# --------------------------------------------------------------------
class GoogleLoginRequest(BaseModel):
    """
    Payload sent from frontend after Google login:

    {
      "id_token": "<google_id_token>"
    }
    """
    id_token: str


class JWTResponse(BaseModel):
    """
    Response sent back to frontend containing YOUR JWT,
    plus (optionally) the user object.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserSchema | None = None


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def _get_user_id(user: UserDB) -> str:
    """Handle user_id vs id field name differences."""
    if hasattr(user, "user_id"):
        return str(user.user_id)
    return str(user.id)


def create_jwt_for_user(user: UserDB) -> str:
    """Create a signed JWT for the given user."""
    now = datetime.utcnow()
    payload = {
        "sub": _get_user_id(user),
        "email": user.email,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    if isinstance(token, bytes):  # just in case
        token = token.decode("utf-8")
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserDB:
    """
    Extract and validate JWT from:
        Authorization: Bearer <token>
    and return the current UserDB instance.

    Used as a dependency on protected endpoints.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Look up the user in the database
    user = db.query(UserDB).filter(UserDB.user_id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user



# --------------------------------------------------------------------
# Route: Google OAuth → your JWT
# --------------------------------------------------------------------
@router.post(
    "/google",
    response_model=JWTResponse,
    summary="Login with Google and receive a JWT",
)
async def google_login(
    body: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    """
    1. Verify Google ID token from frontend.
    2. Find or create user in DB.
    3. Return your own JWT (and user info).
    """

    if not GOOGLE_CLIENT_ID or GOOGLE_CLIENT_ID == "YOUR_GOOGLE_CLIENT_ID_HERE":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID not configured on server",
        )

    # 1️⃣ Verify Google ID token against our client ID
    try:
        idinfo = id_token.verify_oauth2_token(
            body.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

    if idinfo.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token audience does not match client ID",
        )

    email = idinfo.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token does not contain email",
        )

    given_name = idinfo.get("given_name") or ""
    family_name = idinfo.get("family_name") or ""

    # 2️⃣ Find or create user in DB
    user = db.query(UserDB).filter(UserDB.email == email).first()

    if not user:
        user = UserDB(
            email=email,
            first_name=given_name,
            last_name=family_name,
            status="active",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 3️⃣ Create JWT
    access_token = create_jwt_for_user(user)

    # Convert DB user -> Pydantic UserSchema for response
    user_schema = UserSchema.model_validate(user)

    return JWTResponse(access_token=access_token, user=user_schema)
