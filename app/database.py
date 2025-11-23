# # import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# Base = declarative_base()

# # -------------------------------------------------------------------
# # Detect if running in Cloud Run
# # -------------------------------------------------------------------
# RUNNING_IN_CLOUD = os.getenv("K_SERVICE") is not None

# if RUNNING_IN_CLOUD:
#     # ---------------------------------------------------------------
#     # CLOUD RUN → connect via UNIX SOCKET (secure)
#     # ---------------------------------------------------------------
#     INSTANCE_CONNECTION_NAME = os.getenv("users-microservice-db")  # cloud-73905:us-central1:cloudsql-mysql-server
#     DB_USER = os.getenv("DB_USER", "root")
#     DB_PASS = os.getenv("DB_PASS", "")
#     DB_NAME = os.getenv("DB_NAME", "users_db")

#     DATABASE_URL = (
#         f"mysql+pymysql://{DB_USER}:{DB_PASS}"
#         f"@/{DB_NAME}"
#         f"?unix_socket=/cloudsql/{INSTANCE_CONNECTION_NAME}"
#     )

# else:
#     # ---------------------------------------------------------------
#     # LOCAL DEVELOPMENT → connect via PUBLIC IP
#     # ---------------------------------------------------------------
#     DB_HOST = os.getenv("DB_HOST", "34.171.123.10")   # <-- your Cloud SQL public IP
#     DB_USER = os.getenv("DB_USER", "root")
#     DB_PASS = os.getenv("DB_PASS", "")
#     DB_NAME = os.getenv("DB_NAME", "usersdb")

#     DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"


# # -------------------------------------------------------------------
# # Create Engine + Session
# # -------------------------------------------------------------------
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# # Dependency for FastAPI routes
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# -------------------------------------------------------------------
# Detect if running in Cloud Run (Google sets K_SERVICE env var)
# -------------------------------------------------------------------
RUNNING_IN_CLOUD = os.getenv("K_SERVICE") is not None

if RUNNING_IN_CLOUD:
    # ---------------------------------------------------------------
    # CLOUD RUN → connect using UNIX SOCKET (secure method)
    # ---------------------------------------------------------------
    INSTANCE_CONNECTION_NAME = os.getenv(
        "INSTANCE_CONNECTION_NAME",
        "cloud-73905:us-central1:users-microservice-db"
    )

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_NAME = os.getenv("DB_NAME", "users_db")

    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}"
        f"@/{DB_NAME}"
        f"?unix_socket=/cloudsql/{INSTANCE_CONNECTION_NAME}"
    )

else:
    # ---------------------------------------------------------------
    # LOCAL DEV → use PUBLIC IP of Cloud SQL
    # ---------------------------------------------------------------
    DB_HOST = os.getenv("DB_HOST", "34.45.123.82")  # <-- fill in
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_NAME = os.getenv("DB_NAME", "users_db")

    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"


# -------------------------------------------------------------------
# Create SQLAlchemy engine & session
# -------------------------------------------------------------------
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# FastAPI DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
