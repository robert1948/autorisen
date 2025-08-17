from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

# Simple in-memory demo
app = FastAPI(
    title="CapeControl Enhanced Authentication Demo",
    description="Demonstration of the enhanced authentication system",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security setup
SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In-memory storage for demo
users_db = {}
tokens_db = set()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str = None
    last_name: str = None
    role: str = "customer"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    if token not in tokens_db:
        raise HTTPException(status_code=401, detail="Token invalid or expired")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        return users_db[user_id]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Endpoints
@app.post("/api/auth/register", response_model=dict)
async def register(user_data: UserCreate):
    # Check if user exists
    for user in users_db.values():
        if user["email"] == user_data.email:
            raise HTTPException(status_code=409, detail="Email already registered")
    
    # Create user
    user_id = len(users_db) + 1
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "first_name": user_data.first_name or "",
        "last_name": user_data.last_name or "",
        "role": user_data.role,
        "created_at": datetime.utcnow().isoformat()
    }
    
    users_db[user_id] = user
    
    # Create token
    access_token = create_access_token({"sub": str(user_id)})
    tokens_db.add(access_token)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user": UserResponse(**user),
            "tokens": TokenResponse(access_token=access_token)
        }
    }

@app.post("/api/auth/login", response_model=dict)
async def login(login_data: UserLogin):
    # Find user
    user = None
    for u in users_db.values():
        if u["email"] == login_data.email:
            user = u
            break
    
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token({"sub": str(user["id"])})
    tokens_db.add(access_token)
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user": UserResponse(**user),
            "tokens": TokenResponse(access_token=access_token)
        }
    }

@app.get("/api/auth/me", response_model=dict)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "data": UserResponse(**current_user)
    }

@app.post("/api/auth/logout", response_model=dict)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    tokens_db.discard(token)
    return {"success": True, "message": "Logout successful"}

@app.get("/api/auth/developer/earnings", response_model=dict)
async def get_developer_earnings(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "developer":
        raise HTTPException(status_code=403, detail="Developer access required")
    
    # Mock developer earnings data
    return {
        "success": True,
        "data": {
            "summary": {
                "total_revenue_share": 1250.75,
                "total_paid_out": 800.00,
                "pending_payout": 450.75,
                "active_agents": 2,
                "currency": "USD"
            },
            "earnings": [
                {
                    "id": 1,
                    "agent_id": "ai_assistant_v1",
                    "agent_name": "AI Assistant Pro",
                    "revenue_share": 750.50,
                    "total_sales": 2501.67,
                    "commission_rate": 0.3000,
                    "is_active": True
                },
                {
                    "id": 2,
                    "agent_id": "marketing_bot_v2",
                    "agent_name": "Marketing Assistant",
                    "revenue_share": 500.25,
                    "total_sales": 1667.50,
                    "commission_rate": 0.3000,
                    "is_active": True
                }
            ]
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "users_count": len(users_db),
        "active_tokens": len(tokens_db)
    }

@app.get("/")
async def root():
    return {
        "message": "🎉 CapeControl Enhanced Authentication System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "JWT Authentication",
            "Role-based Access Control",
            "Developer Revenue Tracking",
            "Secure Password Hashing",
            "Token Management"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
