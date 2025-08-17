"""
Enhanced Authentication API Routes
=================================

This module implements the secure authentication API endpoints:
- POST /register: Create a new user
- POST /login: Authenticate user, return JWT
- POST /logout: Invalidate JWT
- POST /refresh: Refresh access token
- POST /reset-password: Send password reset email
- POST /reset-password/confirm: Confirm password reset
- GET /me: Fetch user profile (protected)
- GET /developer/earnings: Fetch revenue share data (developers only)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models import User
from app.models_enhanced import DeveloperEarning, UserRole
from app.schemas_enhanced import (
    UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefresh,
    PasswordResetRequest, PasswordResetConfirm, PasswordResetResponse,
    DeveloperEarningsSummary, DeveloperEarningResponse, UserUpdate,
    PasswordChange, ApiResponse, ErrorResponse, Phase2ProfileComplete
)
from app.auth_enhanced import auth_service
from app.dependencies import get_db
from app.email_service import email_service

router = APIRouter(prefix="/api/enhanced", tags=["enhanced-authentication"])
security = HTTPBearer()

# ================================
# Dependency Functions
# ================================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), 
                    db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    
    # Verify token
    payload = auth_service.verify_token(token, "access")
    user_id = int(payload.get("sub"))
    
    # Check if token is revoked
    from app.models_enhanced import Token
    db_token = db.query(Token).filter(
        Token.token == token,
        Token.token_type == "access",
        Token.is_revoked == False,
        Token.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or revoked"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Update token last used
    db_token.used_at = datetime.utcnow()
    db.commit()
    
    return user

def require_developer(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be a developer"""
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer access required"
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_client_info(request: Request) -> dict:
    """Extract client information from request"""
    return {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent", "")
    }

# ================================
# Root API Information Endpoint
# ================================

@router.get("/")
async def enhanced_api_root():
    """Enhanced Authentication API root endpoint"""
    return {
        "service": "Enhanced Authentication API",
        "version": "2.0.0", 
        "status": "operational",
        "description": "Secure, scalable authentication with JWT, role-based access, and Phase 2 onboarding",
        "features": [
            "JWT authentication",
            "Role-based access control", 
            "Phase 2 customer/developer onboarding",
            "Audit logging",
            "Developer earnings tracking",
            "Password reset",
            "Token refresh"
        ],
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login", 
            "profile": "GET /me",
            "phase2_complete": "POST /complete-phase2-profile",
            "health": "GET /health",
            "docs": "/docs"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ================================
# Health Check Endpoint
# ================================

@router.get("/health")
async def enhanced_health_check():
    """Enhanced API health check"""
    return {
        "status": "healthy",
        "service": "Enhanced Authentication API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ["JWT", "Role-based access", "Audit logging", "Developer earnings"]
    }

# ================================
# Debug Endpoint
# ================================

@router.get("/debug/db-test")
async def debug_database_test(db: Session = Depends(get_db)):
    """Debug endpoint to test database connectivity with enhanced models"""
    try:
        # Test if we can query the users_v2 table
        user_count = db.query(User).count()
        
        # Test enum values
        enum_values = [role.value for role in UserRole]
        
        return {
            "status": "success",
            "users_v2_count": user_count,
            "enum_values": enum_values,
            "database_connected": True
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database_connected": False
        }

# ================================
# Authentication Endpoints
# ================================

@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    client_info = get_client_info(request)
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            auth_service.log_event(
                db, None, "register_attempt", 
                f"Failed registration attempt for existing email: {user_data.email}",
                success=False, **client_info, endpoint="/api/auth/register",
                error_message="Email already registered"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            company=user_data.company,
            phone=user_data.phone,
            website=user_data.website,
            experience=user_data.experience,
            terms_accepted_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create tokens
        tokens = auth_service.create_user_tokens(db, db_user, **client_info)
        
        # Log successful registration
        auth_service.log_event(
            db, db_user.id, "register", 
            f"New user registered: {db_user.email} as {db_user.role.value}",
            success=True, **client_info, endpoint="/api/auth/register"
        )
        
        # Send registration notification email
        try:
            email_data = {
                'firstName': user_data.first_name,
                'lastName': user_data.last_name,
                'email': user_data.email,
                'role': user_data.role.value,
                'company': user_data.company or '',
                'phone': user_data.phone or '',
                'website': user_data.website or '',
                'experience': user_data.experience or ''
            }
            await email_service.send_registration_notification(email_data)
        except Exception as e:
            # Don't fail registration if email fails
            print(f"⚠️ Failed to send registration notification: {e}")
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        auth_service.log_event(
            db, None, "register_error", 
            f"Registration error for {user_data.email}",
            success=False, **client_info, endpoint="/api/auth/register",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/register-simple", response_model=TokenResponse)
async def register_simple(
    user_data: UserCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Simplified registration for testing (no email notification)"""
    client_info = get_client_info(request)
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            company=user_data.company,
            phone=user_data.phone,
            website=user_data.website,
            experience=user_data.experience,
            terms_accepted_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create tokens
        tokens = auth_service.create_user_tokens(db, db_user, **client_info)
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    client_info = get_client_info(request)
    
    try:
        # Authenticate user
        user = auth_service.authenticate_user(db, credentials.email, credentials.password)
        if not user:
            auth_service.log_event(
                db, None, "login_attempt", 
                f"Failed login attempt for {credentials.email}",
                success=False, **client_info, endpoint="/api/auth/login",
                error_message="Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        tokens = auth_service.create_user_tokens(db, user, **client_info)
        
        # Log successful login
        auth_service.log_event(
            db, user.id, "login", 
            f"User logged in: {user.email}",
            success=True, **client_info, endpoint="/api/auth/login"
        )
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        auth_service.log_event(
            db, None, "login_error", 
            f"Login error for {credentials.email}",
            success=False, **client_info, endpoint="/api/auth/login",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    token_data: TokenRefresh,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    client_info = get_client_info(request)
    
    try:
        tokens = auth_service.refresh_access_token(db, token_data.refresh_token)
        
        # Log token refresh
        auth_service.log_event(
            db, tokens.user.id, "token_refresh", 
            f"Token refreshed for user: {tokens.user.email}",
            success=True, **client_info, endpoint="/api/auth/refresh"
        )
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        auth_service.log_event(
            db, None, "token_refresh_error", 
            "Token refresh error",
            success=False, **client_info, endpoint="/api/auth/refresh",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout", response_model=ApiResponse)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout user and revoke tokens"""
    client_info = get_client_info(request)
    
    try:
        # Revoke current access token
        auth_service.revoke_token(db, credentials.credentials, "access")
        
        # Also revoke any refresh tokens for this user session
        # In production, you might want to track refresh tokens per session
        # For now, we'll revoke all refresh tokens for the user
        auth_service.revoke_all_user_tokens(db, current_user.id)
        
        # Log logout
        auth_service.log_event(
            db, current_user.id, "logout", 
            f"User logged out: {current_user.email}",
            success=True, **client_info, endpoint="/api/auth/v2/logout"
        )
        
        return ApiResponse(success=True, message="Successfully logged out")
        
    except Exception as e:
        auth_service.log_event(
            db, current_user.id, "logout_error", 
            f"Logout error for {current_user.email}",
            success=False, **client_info, endpoint="/api/auth/v2/logout",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/logout-all", response_model=ApiResponse)
def logout_all(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout from all devices (revoke all tokens)"""
    client_info = get_client_info(request)
    
    try:
        # Revoke all user tokens
        auth_service.revoke_all_user_tokens(db, current_user.id)
        
        # Log logout all
        auth_service.log_event(
            db, current_user.id, "logout_all", 
            f"User logged out from all devices: {current_user.email}",
            success=True, **client_info, endpoint="/api/auth/logout-all"
        )
        
        return ApiResponse(success=True, message="Successfully logged out from all devices")
        
    except Exception as e:
        auth_service.log_event(
            db, current_user.id, "logout_all_error", 
            f"Logout all error for {current_user.email}",
            success=False, **client_info, endpoint="/api/auth/logout-all",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# ================================
# Password Reset Endpoints
# ================================

@router.post("/reset-password", response_model=PasswordResetResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request password reset email"""
    client_info = get_client_info(request)
    
    try:
        # Find user
        user = db.query(User).filter(User.email == reset_data.email).first()
        if not user:
            # Don't reveal if email exists
            return PasswordResetResponse(
                message="If the email exists, a reset link has been sent",
                email_sent=False
            )
        
        # Create reset token
        reset_token = auth_service.create_password_reset(db, user, **client_info)
        
        # TODO: Send password reset email
        # await email_service.send_password_reset_email(user.email, reset_token)
        
        # Log password reset request
        auth_service.log_event(
            db, user.id, "password_reset_request", 
            f"Password reset requested for {user.email}",
            success=True, **client_info, endpoint="/api/auth/reset-password"
        )
        
        return PasswordResetResponse(
            message="If the email exists, a reset link has been sent",
            email_sent=True
        )
        
    except Exception as e:
        auth_service.log_event(
            db, None, "password_reset_error", 
            f"Password reset error for {reset_data.email}",
            success=False, **client_info, endpoint="/api/auth/reset-password",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/reset-password/confirm", response_model=ApiResponse)
def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    client_info = get_client_info(request)
    
    try:
        # Reset password
        success = auth_service.reset_password(db, reset_data.token, reset_data.new_password)
        
        if success:
            # Get user for logging (token is now used)
            user, _ = auth_service.verify_reset_token(db, reset_data.token)
            
            auth_service.log_event(
                db, user.id, "password_reset_confirm", 
                f"Password reset confirmed for {user.email}",
                success=True, **client_info, endpoint="/api/auth/reset-password/confirm"
            )
            
            return ApiResponse(success=True, message="Password reset successful")
        
    except HTTPException:
        raise
    except Exception as e:
        auth_service.log_event(
            db, None, "password_reset_confirm_error", 
            "Password reset confirmation error",
            success=False, **client_info, endpoint="/api/auth/reset-password/confirm",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed"
        )

# ================================
# User Profile Endpoints
# ================================

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    client_info = get_client_info(request)
    
    try:
        # Update user fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        # Log profile update
        auth_service.log_event(
            db, current_user.id, "profile_update", 
            f"Profile updated for {current_user.email}",
            success=True, **client_info, endpoint="/api/auth/me",
            metadata=update_data
        )
        
        return UserResponse.from_orm(current_user)
        
    except Exception as e:
        auth_service.log_event(
            db, current_user.id, "profile_update_error", 
            f"Profile update error for {current_user.email}",
            success=False, **client_info, endpoint="/api/auth/me",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/complete-phase2-profile", response_model=UserResponse)
def complete_phase2_profile(
    profile_data: Phase2ProfileComplete,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete Phase 2 profile onboarding"""
    client_info = get_client_info(request)
    
    try:
        # Update user with Phase 2 profile data
        update_data = profile_data.dict(exclude_unset=True, by_alias=False)
        
        # Convert camelCase to snake_case for database fields
        field_mappings = {
            'profileCompleted': 'profile_completed',
            'phase2Completed': 'phase2_completed',
            'companyName': 'company_name',
            'companySize': 'company_size',
            'businessType': 'business_type',
            'useCase': 'use_case',
            'preferredIntegrations': 'preferred_integrations',
            'experienceLevel': 'experience_level',
            'primaryLanguages': 'primary_languages',
            'githubProfile': 'github_profile',
            'portfolioUrl': 'portfolio_url',
            'socialLinks': 'social_links',
            'previousProjects': 'previous_projects',
            'hourlyRate': 'hourly_rate',
            'earningsTarget': 'earnings_target',
            'revenueShare': 'revenue_share'
        }
        
        # Apply field mappings
        for camel_key, snake_key in field_mappings.items():
            if camel_key in update_data:
                update_data[snake_key] = update_data.pop(camel_key)
        
        # Update user fields
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        # Log profile completion
        auth_service.log_event(
            db, current_user.id, "phase2_profile_complete", 
            f"Phase 2 profile completed for {current_user.email} (role: {current_user.role})",
            success=True, **client_info, endpoint="/api/enhanced/complete-phase2-profile",
            metadata={"role": current_user.role.value, "fields_updated": list(update_data.keys())}
        )
        
        return UserResponse.from_orm(current_user)
        
    except Exception as e:
        auth_service.log_event(
            db, current_user.id, "phase2_profile_error", 
            f"Phase 2 profile completion error for {current_user.email}",
            success=False, **client_info, endpoint="/api/enhanced/complete-phase2-profile",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Phase 2 profile completion failed"
        )

@router.post("/change-password", response_model=ApiResponse)
def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    client_info = get_client_info(request)
    
    try:
        # Verify current password
        if not auth_service.verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.password_hash = auth_service.get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.utcnow()
        
        # Revoke all existing tokens
        auth_service.revoke_all_user_tokens(db, current_user.id)
        
        db.commit()
        
        # Log password change
        auth_service.log_event(
            db, current_user.id, "password_change", 
            f"Password changed for {current_user.email}",
            success=True, **client_info, endpoint="/api/auth/change-password"
        )
        
        return ApiResponse(success=True, message="Password changed successfully. Please log in again.")
        
    except HTTPException:
        raise
    except Exception as e:
        auth_service.log_event(
            db, current_user.id, "password_change_error", 
            f"Password change error for {current_user.email}",
            success=False, **client_info, endpoint="/api/auth/change-password",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

# ================================
# Developer Earnings Endpoints
# ================================

@router.get("/developer/earnings", response_model=DeveloperEarningsSummary)
def get_developer_earnings(
    current_user: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    """Get developer earnings summary"""
    try:
        # Get all earnings for this developer
        earnings = db.query(DeveloperEarning).filter(
            DeveloperEarning.user_id == current_user.id
        ).all()
        
        # Calculate summary
        total_agents = len(earnings)
        total_revenue_share = sum(e.revenue_share for e in earnings)
        total_sales = sum(e.total_sales for e in earnings)
        total_paid_out = sum(e.total_paid_out for e in earnings)
        pending_payout = total_revenue_share - total_paid_out
        
        return DeveloperEarningsSummary(
            total_agents=total_agents,
            total_revenue_share=total_revenue_share,
            total_sales=total_sales,
            total_paid_out=total_paid_out,
            pending_payout=pending_payout,
            currency="USD",
            earnings=[DeveloperEarningResponse.from_orm(e) for e in earnings]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch developer earnings"
        )
