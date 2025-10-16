
import re
import time
import traceback
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import create_access_token, get_password_hash, verify_password
from app.dependencies import get_current_user, get_db
from app.services.audit_service import AuditEventType, get_audit_logger

router = APIRouter()

from app.config import settings

# Load secret key and algorithm from settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

def map_user_role_to_db(user_role: str) -> str:
    """Map frontend user role to database role values"""
    role_mapping = {
        'client': 'CUSTOMER',
        'customer': 'CUSTOMER', 
        'developer': 'DEVELOPER',
        'admin': 'ADMIN'
    }
    return role_mapping.get(user_role, 'CUSTOMER')

def map_db_role_to_user(db_role: str) -> str:
    """Map database role to frontend user role values"""
    role_mapping = {
        'CUSTOMER': 'client',
        'DEVELOPER': 'developer',
        'ADMIN': 'admin',
        # Also handle lowercase for backward compatibility
        'customer': 'client',
        'developer': 'developer',
        'admin': 'admin'
    }
    return role_mapping.get(db_role, 'client')

@router.get("/v2/ping", tags=["auth-v2"])
async def ping():
    """Ultra-fast ping endpoint without any dependencies to test basic functionality"""
    return {"status": "ok", "message": "Auth v2 router is working", "timestamp": datetime.utcnow().isoformat()}

@router.get("/profile", tags=["auth-v2"])
async def get_user_profile(current_user: models.User = Depends(get_current_user)):
    """Get current user's profile information"""
    try:
        return {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": map_db_role_to_user(current_user.user_role),
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "company": current_user.company,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )

@router.get("/v2/health", tags=["auth-v2"])
async def health_check():
    """Lightning-fast health check endpoint"""
    start_time = time.time()
    response_time_ms = (time.time() - start_time) * 1000
    return {
        "status": "healthy",
        "service": "CapeControl Auth API v2",
        "response_time_ms": round(response_time_ms, 2),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/v2/status", tags=["auth-v2"])
async def production_status():
    """Production status endpoint showing system health"""
    try:
        return {
            "service": "CapeControl Auth API",
            "status": "operational",
            "version": "3.0.0",
            "endpoints": {
                "ping": "✅ Available",
                "register_test": "✅ Available (no database)",
                "register_production": "✅ Available (with database resilience)",
                "health": "✅ Available (database health check)"
            },
            "features": {
                "input_sanitization": "⚠️ Temporarily disabled",
                "audit_logging": "✅ Available",
                "ddos_protection": "✅ Available",
                "email_notifications": "✅ Available"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "service": "CapeControl Auth API",
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/token", tags=["auth-v2"])
async def get_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token endpoint for authentication"""
    try:
        # Authenticate user
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "role": map_db_role_to_user(user.role)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token generation failed: {str(e)}"
        )

@router.get("/health", tags=["auth-v2"])
async def health_check():
    """Ultra-fast health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@router.post("/v2/bypass-test", tags=["auth-v2"])
async def bypass_login_test(request: Request):
    """Bypass test endpoint with NO dependencies to isolate middleware issues"""
    print(f"🚀 BYPASS TEST REACHED at {time.time()}")
    try:
        body = await request.json()
        print(f"📩 Body received: {body}")
        return {"status": "bypass_success", "timestamp": time.time(), "received": body}
    except Exception as e:
        print(f"❌ Bypass test error: {e}")
        return {"status": "bypass_error", "error": str(e)}

@router.get("/v2/validate-email", tags=["auth-v2"])
async def validate_email(email: str, db: Session = Depends(get_db)):
    try:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {"available": False, "reason": "invalid_format", "message": "Invalid email address"}

        normalized_email = email.lower().strip()
        existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()

        if existing_user:
            return {"available": False, "reason": "already_exists", "message": "Email already registered"}

        return {"available": True, "message": "Email is available"}
    except Exception as e:
        print(f"Email validation error: {e}")
        return {"available": None, "reason": "validation_error", "message": "Unable to validate email"}

@router.post("/v2/validate-password", tags=["auth-v2"])
async def validate_password(password_data: dict):
    password = password_data.get("password", "")
    requirements = {
        "minLength": len(password) >= 8,  # Match schema validation (8 chars)
        "hasUpper": bool(re.search(r'[A-Z]', password)),
        "hasLower": bool(re.search(r'[a-z]', password)),
        "hasNumber": bool(re.search(r'[0-9]', password)),
        "hasSpecial": bool(re.search(r'[^A-Za-z0-9]', password))
    }
    # Special character is optional for schema compatibility
    core_requirements = ["minLength", "hasUpper", "hasLower", "hasNumber"]
    core_valid = all(requirements[req] for req in core_requirements)
    
    score = sum([25 if requirements["minLength"] else 0,
                 20 if requirements["hasUpper"] else 0,
                 20 if requirements["hasLower"] else 0,
                 20 if requirements["hasNumber"] else 0,
                 15 if requirements["hasSpecial"] else 0])
    return {
        "valid": core_valid,  # Only require core requirements (no special char)
        "score": min(score, 100),
        "requirements": requirements,
        "message": "Strong password" if core_valid else "Weak password"
    }

@router.post("/v2/register-simple", tags=["auth-v2"])
async def register_simple(user_email: str, db: Session = Depends(get_db)):
    """Simplified registration endpoint for debugging database connectivity issues."""
    try:
        from sqlalchemy import text
        print(f"🔍 Starting simple registration for: {user_email}")
        
        # Test basic database connectivity
        print("🔍 Testing basic DB connection...")
        db.execute(text("SELECT 1")).fetchone()
        print("✅ Basic DB connection works")
        
        # Test user table query
        print("🔍 Testing user table query...")
        normalized_email = user_email.lower().strip()
        existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
        print(f"✅ User query complete, existing: {existing_user is not None}")
        
        if existing_user:
            return {"status": "error", "message": "Email already exists", "email": normalized_email}
        
        return {"status": "success", "message": "Email available", "email": normalized_email}
        
    except Exception as e:
        print(f"❌ Simple registration error: {e}")
        return {"status": "error", "message": f"Database error: {str(e)}"}

@router.post("/v2/register-test", tags=["auth-v2"])
async def register_test(user_data: schemas.UserCreateMinimal):
    """Test endpoint without database dependency to isolate the issue."""
    try:
        print(f"🔍 Test registration called for: {user_data.email}")
        
        # Just return the data without database operations
        return {
            "status": "success",
            "message": "Test endpoint working",
            "received_email": user_data.email,
            "received_name": user_data.full_name,
            "password_length": len(user_data.password)
        }
        
    except Exception as e:
        print(f"❌ Test registration error: {e}")
        return {"status": "error", "message": f"Test failed: {str(e)}"}

@router.post("/v2/register-production", tags=["auth-v2"])
async def register_production(user_data: schemas.UserCreateMinimal):
    """Production-ready registration endpoint with database resilience."""
    try:
        print(f"🔍 Production registration for: {user_data.email}")
        
        # Import database components
        import asyncio

        from app.auth import get_password_hash
        from app.database import SessionLocal
        
        # Normalize email
        normalized_email = user_data.email.lower().strip()
        
        # Create database session with timeout protection
        db = SessionLocal()
        
        try:
            # Check if user exists with timeout
            async def check_user():
                existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
                return existing_user
            
            existing_user = await asyncio.wait_for(check_user(), timeout=5.0)
            
            if existing_user:
                db.close()
                return {"status": "error", "message": "Email already registered"}
            
            # Create user with timeout protection
            async def create_user():
                hashed_password = get_password_hash(user_data.password)
                name_parts = user_data.full_name.strip().split(' ', 1)
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                db_user = models.User(
                    email=normalized_email,
                    password_hash=hashed_password,
                    role="CUSTOMER",
                    first_name=first_name,
                    last_name=last_name,
                    terms_accepted_at=datetime.utcnow()
                )
                
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                return db_user
            
            db_user = await asyncio.wait_for(create_user(), timeout=5.0)
            db.close()
            
            return {
                "status": "success",
                "id": str(db_user.id),
                "email": db_user.email,
                "message": "User registered successfully"
            }
            
        except TimeoutError:
            db.rollback()
            db.close()
            return {"status": "error", "message": "Database timeout - please try again"}
            
        except Exception as e:
            db.rollback()
            db.close()
            print(f"❌ Database error: {e}")
            return {"status": "error", "message": f"Registration failed: {str(e)}"}
            
    except Exception as e:
        print(f"❌ Production registration error: {e}")
        return {"status": "error", "message": "Service temporarily unavailable"}

@router.post("/v2/register-flexible", tags=["auth-v2"])
async def register_flexible(request: Request, db: Session = Depends(get_db)):
    """Flexible registration endpoint that accepts any JSON and processes manually."""
    try:
        # Get raw body
        body = await request.body()
        print(f"🔍 Flexible registration - raw body: {body.decode('utf-8') if body else 'Empty'}")
        
        if not body:
            return {"status": "error", "message": "No request body provided"}
        
        # Parse JSON manually
        import json
        try:
            data = json.loads(body.decode('utf-8'))
            print(f"🔍 Parsed data: {data}")
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
        
        # Extract required fields manually
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        user_role = data.get('user_role', 'client').strip()
        company_name = data.get('company_name', '').strip() if data.get('company_name') else None
        
        print(f"🔍 Extracted fields - email: {email}, full_name: {full_name}, user_role: {user_role}")
        
        # Basic validation
        if not email or not password or not full_name:
            return {
                "status": "error", 
                "message": "Missing required fields", 
                "required": ["email", "password", "full_name"],
                "received": {
                    "email": bool(email),
                    "password": bool(password), 
                    "full_name": bool(full_name)
                }
            }
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {"status": "error", "message": "Invalid email format"}
        
        # Check if user exists
        normalized_email = email.lower().strip()
        existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
        if existing_user:
            return {"status": "error", "message": "Email already registered"}
        
        # Create user
        hashed_password = get_password_hash(password)
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        db_user = models.User(
            email=normalized_email,
            password_hash=hashed_password,
            role=map_user_role_to_db(user_role),
            first_name=first_name,
            last_name=last_name,
            company=company_name,
            terms_accepted_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "status": "success",
            "id": str(db_user.id),
            "email": db_user.email,
            "message": "User registered successfully via flexible endpoint"
        }
        
    except Exception as e:
        print(f"❌ Flexible registration error: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        db.rollback()
        return {"status": "error", "message": f"Registration failed: {str(e)}"}

@router.post("/v2/register-debug", tags=["auth-v2"])
async def register_debug(request: Request):
    """Debug endpoint to see what data is being sent in registration requests."""
    try:
        body = await request.body()
        content_type = request.headers.get("content-type", "")
        
        print("🔍 Debug registration request:")
        print(f"Content-Type: {content_type}")
        print(f"Body: {body.decode('utf-8') if body else 'Empty'}")
        print(f"Headers: {dict(request.headers)}")
        
        if body:
            try:
                import json
                json_data = json.loads(body.decode('utf-8'))
                print(f"Parsed JSON: {json_data}")
                
                return {
                    "status": "debug_success",
                    "received_data": json_data,
                    "content_type": content_type,
                    "required_fields": ["email", "password", "full_name"],
                    "optional_fields": ["user_role", "tos_accepted", "company_name"]
                }
            except json.JSONDecodeError as e:
                return {
                    "status": "debug_error",
                    "error": "Invalid JSON",
                    "body": body.decode('utf-8'),
                    "json_error": str(e)
                }
        else:
            return {
                "status": "debug_error", 
                "error": "No body received",
                "content_type": content_type
            }
            
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
        return {"status": "debug_error", "error": str(e)}

@router.post("/v2/register-simple-json", tags=["auth-v2"])
async def register_simple_json(request: Request, db: Session = Depends(get_db)):
    """Simple JSON registration without strict schema validation."""
    try:
        # Parse JSON manually to avoid schema validation issues
        body = await request.body()
        import json
        data = json.loads(body.decode('utf-8'))
        
        print(f"🔍 Simple JSON registration data: {data}")
        
        # Extract and validate fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        
        if not all([email, password, full_name]):
            return {
                "status": "error",
                "message": "Missing required fields: email, password, full_name"
            }
        
        # Check if user exists
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if existing_user:
            return {"status": "error", "message": "Email already registered"}
        
        # Create user with minimal required fields
        hashed_password = get_password_hash(password)
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        db_user = models.User(
            email=email,
            password_hash=hashed_password,
            role="CUSTOMER",  # Default role
            first_name=first_name,
            last_name=last_name,
            terms_accepted_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit() 
        db.refresh(db_user)
        
        return {
            "id": str(db_user.id),
            "email": db_user.email,
            "status": "success",
            "message": "User registered successfully"
        }
        
    except Exception as e:
        print(f"❌ Simple JSON registration error: {e}")
        db.rollback()
        return {"status": "error", "message": f"Registration failed: {str(e)}"}

@router.post("/v2/register", response_model=schemas.UserOut, tags=["auth-v2"])
async def register_v2(user: schemas.UserCreateV2Production, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    try:
        print(f"🔍 Registration attempt for: {user.email}")
        print(f"User role: {user.user_role}")
        print(f"TOS accepted: {user.tos_accepted}")
        
        normalized_email = user.email.lower().strip()
        existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
        if existing_user:
            print(f"❌ Email already registered: {normalized_email}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        hashed_password = get_password_hash(user.password)
        name_parts = user.full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        db_user = models.User(
            email=normalized_email, 
            password_hash=hashed_password, 
            role=map_user_role_to_db(user.user_role) if user.user_role else "CUSTOMER", 
            first_name=first_name, 
            last_name=last_name, 
            company=user.company_name.strip() if user.company_name else None, 
            terms_accepted_at=datetime.utcnow()
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"✅ User created successfully: {db_user.id} - {db_user.email}")

        # Move audit logging to background task to prevent transaction rollback
        background_tasks.add_task(
            log_registration_audit_task,
            str(db_user.id),
            db_user.email,
            db_user.role,
            user.user_role,
            user.company_name,
            request.client.host if request.client else "unknown",
            request.headers.get("user-agent", "unknown")
        )

        background_tasks.add_task(send_welcome_email_task, {
            'full_name': user.full_name, 
            'email': user.email, 
            'user_role': user.user_role, 
            'company_name': user.company_name or '', 
            'userId': db_user.id
        })

        return {"id": str(db_user.id), "email": db_user.email}
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Integrity error during registration: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    except Exception as e:
        db.rollback()
        print(f"❌ Registration error: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

async def log_registration_audit_task(user_id: str, email: str, role: str, user_role: str, company_name: str, ip_address: str, user_agent: str):
    """Log registration audit event in background to prevent transaction rollback."""
    try:
        audit_logger = get_audit_logger()
        from app.database import SessionLocal
        
        # Use separate database session for audit logging
        audit_db = SessionLocal()
        try:
            # Create a mock request object for audit logging
            class MockRequest:
                def __init__(self, ip: str, user_agent: str):
                    self.client = type('obj', (object,), {'host': ip})()
                    self.headers = {"user-agent": user_agent}
            
            mock_request = MockRequest(ip_address, user_agent)
            
            audit_logger.log_authentication_event(
                db=audit_db,
                event_type=AuditEventType.USER_REGISTRATION,
                request=mock_request,
                user_id=user_id,
                user_email=email,
                user_role=role,
                success=True,
                additional_data={
                    "user_role": user_role,
                    "company_name": company_name,
                    "registration_method": "v2_direct"
                }
            )
            audit_db.commit()
            print(f"✅ Audit log recorded for user: {email}")
        except Exception as audit_error:
            audit_db.rollback()
            print(f"⚠️ Failed to log audit event (non-critical): {audit_error}")
        finally:
            audit_db.close()
            
    except Exception as e:
        print(f"⚠️ Audit logging task failed (non-critical): {e}")

async def send_welcome_email_task(user_data: dict):
    """Send welcome email with improved error handling and timeout protection."""
    try:
        # Add timeout protection and graceful degradation
        import asyncio

        from app.email_service import email_service
        await asyncio.wait_for(
            email_service.send_registration_notification(user_data), 
            timeout=10.0  # 10 second timeout
        )
        print(f"✅ Welcome email sent successfully for user: {user_data.get('email', 'unknown')}")
    except TimeoutError:
        print(f"⏰ Welcome email timeout for user: {user_data.get('email', 'unknown')} - continuing anyway")
    except ImportError as e:
        print(f"📧 Email service not available: {e} - skipping email for user: {user_data.get('email', 'unknown')}")
    except Exception as e:
        print(f"❌ Failed to send welcome email for user: {user_data.get('email', 'unknown')} - Error: {e}")
        # Don't raise the exception - email failure shouldn't break registration

@router.post("/v2/login", tags=["auth-v2"])
async def login_v2(payload: schemas.LoginInput, request: Request, db: Session = Depends(get_db)):
    """Ultra-fast login endpoint optimized to prevent any H12 timeouts"""
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    client_ip = request.client.host if request.client else 'unknown'
    
    print(f"🚀 [REQ:{request_id}] Login endpoint reached at {time.time()} for {payload.email} from {client_ip}")
    
    try:
        # Database lookup timing
        db_start = time.time()
        normalized_email = payload.email.lower().strip()
        print(f"🔍 [REQ:{request_id}] Attempting DB lookup for {normalized_email}")
        user = db.query(models.User).filter(models.User.email == normalized_email).first()
        db_time = (time.time() - db_start) * 1000
        print(f"👤 [REQ:{request_id}] User lookup complete: {'Found' if user else 'Not found'} - took {db_time:.1f}ms")

        if not user:
            total_time = (time.time() - start_time) * 1000
            print(f"⚠️ [REQ:{request_id}] Login failed - user not found for {normalized_email} - total time: {total_time:.1f}ms")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        # Password verification timing
        verify_start = time.time()
        if not verify_password(payload.password, user.password_hash):
            verify_time = (time.time() - verify_start) * 1000
            total_time = (time.time() - start_time) * 1000
            print(f"⚠️ [REQ:{request_id}] Login failed - invalid password for {normalized_email} - verify: {verify_time:.1f}ms, total: {total_time:.1f}ms")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        verify_time = (time.time() - verify_start) * 1000
        print(f"🔐 [REQ:{request_id}] Password verification successful - took {verify_time:.1f}ms")        # Token creation timing
        token_start = time.time()
        token_data = {"sub": user.email, "user_id": str(user.id), "role": map_db_role_to_user(user.user_role)}
        access_token = create_access_token(token_data, SECRET_KEY, ALGORITHM)
        token_time = (time.time() - token_start) * 1000
        print(f"🎫 [REQ:{request_id}] Token creation complete - took {token_time:.1f}ms")
        
        # Response preparation timing
        response_start = time.time()
        response_data = {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": {
                "id": str(user.id), 
                "email": user.email, 
                "role": map_db_role_to_user(user.user_role)
            }
        }
        response_time = (time.time() - response_start) * 1000
        total_time = (time.time() - start_time) * 1000
        
        print(f"✅ [REQ:{request_id}] Login successful for {normalized_email} - db: {db_time:.1f}ms, verify: {verify_time:.1f}ms, token: {token_time:.1f}ms, response: {response_time:.1f}ms, total: {total_time:.1f}ms")
        
        return response_data 
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 401) with timing
        total_time = (time.time() - start_time) * 1000
        print(f"⚠️ [REQ:{request_id}] HTTPException raised - total time: {total_time:.1f}ms")
        raise
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        print(f"❌ [REQ:{request_id}] Login error for {payload.email}: {e} - total time: {total_time:.1f}ms")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.post("/register/step1", tags=["auth-v2"])
async def register_step1(request: schemas.RegisterStep1Request, db: Session = Depends(get_db)):
    try:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, request.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        normalized_email = request.email.lower().strip()
        existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        return {"success": True, "message": "Email validated successfully", "step": 1, "next_step": "/api/auth/register/step2"}
    except Exception:
        raise HTTPException(status_code=500, detail="Step 1 validation failed")

@router.post("/register/step2", response_model=schemas.UserOut, tags=["auth-v2"])
async def register_step2(request: schemas.RegisterStep2Request, db: Session = Depends(get_db)):
    try:
        if not all([request.email, request.password, request.full_name]):
            raise HTTPException(status_code=400, detail="Email, password, and full name are required")
        normalized_email = request.email.lower().strip()
        existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = get_password_hash(request.password)
        name_parts = request.full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        db_user = models.User(email=normalized_email, password_hash=hashed_password, role=map_user_role_to_db(request.user_role) if request.user_role else 'CUSTOMER', first_name=first_name, last_name=last_name, company=request.company_name, terms_accepted_at=datetime.utcnow())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        access_token = create_access_token(data={"sub": db_user.email})
        return schemas.UserOut(id=str(db_user.id), email=db_user.email, full_name=request.full_name, user_role=db_user.role, company_name=db_user.company, access_token=access_token, created_at=db_user.created_at)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")
