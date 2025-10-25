"""
Standalone Enhanced Authentication API for Heroku
================================================

This is a production-ready version of the enhanced authentication system that can
run on Heroku without conflicting with the existing user system.

Features:
- Uses v2 table names to avoid conflicts
- Production database support
- Heroku-compatible configuration
- Standalone operation
"""

import enum
import logging
import os
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv(
    "SECRET_KEY", "your-super-secure-secret-key-change-this-in-production"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    # Fallback for development
    DATABASE_URL = "sqlite:///./capecontrol_enhanced.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Models using v2 table names to avoid conflicts
class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    DEVELOPER = "developer"
    ADMIN = "admin"


class UserV2(Base):
    __tablename__ = "users_v2"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DeveloperEarningV2(Base):
    __tablename__ = "developer_earnings_v2"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key handled in migration
    agent_id = Column(String(100), nullable=False)
    agent_name = Column(String(255))
    revenue_share = Column(Numeric(10, 2), default=0.00)
    total_sales = Column(Numeric(10, 2), default=0.00)
    commission_rate = Column(Numeric(5, 4), default=0.3000)
    is_active = Column(Boolean, default=True)
    currency = Column(String(3), default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole = UserRole.CUSTOMER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        # Allow None values for optional fields
        validate_assignment = True


# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI app
app = FastAPI(
    title="CapeControl Enhanced Authentication API",
    description="Production-ready authentication system with developer revenue tracking",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# Helper function to get current user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = verify_token(credentials.credentials)
    user = db.query(UserV2).filter(UserV2.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# Routes
@app.get("/")
async def root():
    return {
        "message": "🎉 CapeControl Enhanced Authentication API v2.0",
        "status": "operational",
        "features": [
            "JWT Authentication",
            "Role-based Access Control",
            "Developer Revenue Tracking",
            "Production Ready",
        ],
        "endpoints": {
            "register": "/auth/register",
            "login": "/auth/login",
            "profile": "/auth/me",
            "developer_earnings": "/auth/developer/earnings",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        user_count = db.query(UserV2).count()
        earnings_count = db.query(DeveloperEarningV2).count()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": "connected",
            "users": user_count,
            "developer_earnings": earnings_count,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow()}


@app.post("/auth/register", response_model=dict)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(UserV2).filter(UserV2.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = UserV2(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user": UserResponse.from_orm(db_user),
            "tokens": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            },
        },
    }


@app.post("/auth/login", response_model=dict)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserV2).filter(UserV2.email == user_login.email).first()
    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user": UserResponse.from_orm(user),
            "tokens": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            },
        },
    }


@app.get("/auth/me", response_model=dict)
async def get_current_user_profile(current_user: UserV2 = Depends(get_current_user)):
    return {"success": True, "data": UserResponse.from_orm(current_user)}


@app.get("/auth/developer/earnings", response_model=dict)
async def get_developer_earnings(
    current_user: UserV2 = Depends(get_current_user), db: Session = Depends(get_db)
):
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(status_code=403, detail="Developer access required")

    earnings = (
        db.query(DeveloperEarningV2)
        .filter(DeveloperEarningV2.user_id == current_user.id)
        .all()
    )

    total_revenue = sum(float(e.revenue_share) for e in earnings)
    active_agents = len([e for e in earnings if e.is_active])

    return {
        "success": True,
        "data": {
            "summary": {
                "total_revenue_share": total_revenue,
                "active_agents": active_agents,
                "currency": "USD",
            },
            "earnings": [
                {
                    "id": e.id,
                    "agent_id": e.agent_id,
                    "agent_name": e.agent_name,
                    "revenue_share": float(e.revenue_share),
                    "total_sales": float(e.total_sales),
                    "commission_rate": float(e.commission_rate),
                    "is_active": e.is_active,
                }
                for e in earnings
            ],
        },
    }


# Create tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Try to create tables (will be ignored if they exist)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Enhanced authentication API started successfully")

        # Create sample data if database is empty
        db = SessionLocal()
        try:
            user_count = db.query(UserV2).count()
            if user_count == 0:
                # Create sample admin user
                admin_user = UserV2(
                    email="admin@capecontrol.com",
                    password_hash=get_password_hash("AdminPassword123!"),
                    role=UserRole.ADMIN,
                    first_name="System",
                    last_name="Administrator",
                    is_active=True,
                    is_verified=True,
                )
                db.add(admin_user)

                # Create sample developer
                dev_user = UserV2(
                    email="developer@capecontrol.com",
                    password_hash=get_password_hash("DevPassword123!"),
                    role=UserRole.DEVELOPER,
                    first_name="Sample",
                    last_name="Developer",
                    is_active=True,
                    is_verified=True,
                )
                db.add(dev_user)
                db.commit()
                db.refresh(dev_user)

                # Create sample earnings
                earnings = DeveloperEarningV2(
                    user_id=dev_user.id,
                    agent_id="ai_assistant_pro",
                    agent_name="AI Assistant Pro",
                    revenue_share=1250.75,
                    total_sales=4169.17,
                    commission_rate=0.3000,
                    is_active=True,
                )
                db.add(earnings)
                db.commit()

                logger.info("✅ Sample data created")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
