from datetime import datetime, timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.database import get_db

# 🔴 IMPORTANT: adjust this import to match your project
# If your model file is different, e.g. app.models.user_model, change it here.
from app.models.user import User as UserDB  # <-- tweak if needed


router = APIRouter()

# ---------------------------------------------------------------------------
# Config (use env vars in Cloud Run)
# ---------------------------------------------------------------------------

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID_HERE")

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class GoogleLoginRequest(BaseModel):
    """
    Body sent by the frontend after Google login.

    {
      "id_token": "<google_id_token_from_frontend>"
    }
    """
    id_token: str


class JWTResponse(BaseModel):
    """
    Response returned to the frontend containing *your* JWT.
    """
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Helper: create our own JWT
# ---------------------------------------------------------------------------

def _get_user_id(user: UserDB) -> str:
    """
    Helper in case your PK field name is user_id vs id.
    Adjust if your model uses a different primary key name.
    """
    return str(getattr(user, "user_id", getattr(user, "id")))


def create_jwt_for_user(user: UserDB) -> str:
    """
    Create a signed JWT for the given user.
    """
    now = datetime.utcnow()
    payload = {
        "sub": _get_user_id(user),
        "email": user.email,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    # PyJWT >= 2 returns a str; older versions may return bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


# ---------------------------------------------------------------------------
# Route: Google OAuth → our JWT
# ---------------------------------------------------------------------------

@router.post("/google", response_model=JWTResponse, summary="Login with Google and get JWT")
async def google_login(
    body: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    """
    1. Verify Google ID token.
    2. Find or create the user in our database.
    3. Return our own JWT to the client.
    """

    if not GOOGLE_CLIENT_ID or GOOGLE_CLIENT_ID == "YOUR_GOOGLE_CLIENT_ID_HERE":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID not configured on server",
        )

    # 1️⃣ Verify Google ID token
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

    # Optional extra safety: ensure audience matches
    aud = idinfo.get("aud")
    if aud != GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token audience does not match client ID",
        )

    email = idinfo.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token did not contain an email",
        )

    given_name = idinfo.get("given_name") or ""
    family_name = idinfo.get("family_name") or ""

    # 2️⃣ Find or create user in our DB
    user = db.query(UserDB).filter(UserDB.email == email).first()

    if not user:
        # Adjust fields to match your actual UserDB model
        user = UserDB(
            email=email,
            first_name=given_name,
            last_name=family_name,
            status="active",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 3️⃣ Issue our JWT
    access_token = create_jwt_for_user(user)

    return JWTResponse(access_token=access_token)
