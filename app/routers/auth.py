# auth_routes.py - Fixed with debugging
from datetime import datetime

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.auth import (create_access_token, decode_access_token,
                           get_password_hash, verify_password)
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter()


class LoginRequest(BaseModel):
    username: str  # This could be username OR email
    password: str


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists by email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists (if you have unique usernames)
    if hasattr(User, 'username') and db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Hash password
    hashed_password = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user with username/email and password."""
    print(f"🔐 Login attempt for: {request.username}")
    
    # Try to find user by email first, then by username
    user = db.query(User).filter(User.email == request.username).first()
    
    # If not found by email, try username (if your User model has a username field)
    if not user and hasattr(User, 'username'):
        user = db.query(User).filter(User.username == request.username).first()
        print(f"👤 Searching by username: {user is not None}")
    else:
        print(f"📧 Found by email: {user is not None}")
    
    if not user:
        print(f"❌ User not found: {request.username}")
        raise HTTPException(status_code=400, detail="User not found")
    
    print(f"🔍 User found: ID={user.id}, Email={user.email}")
    
    # Verify password
    password_valid = verify_password(request.password, user.password)
    print(f"🔑 Password valid: {password_valid}")
    
    if not password_valid:
        print("❌ Invalid password")
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Create token
    token_payload = {"user_id": user.id}
    token = create_access_token(token_payload)
    print(f"🎫 Token created for user {user.id}")
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user_id": user.id  # Add this for debugging
    }


@router.get("/debug-token")
async def debug_token(request: Request, db: Session = Depends(get_db)):
    """Debug route to test your specific token."""
    from fastapi import Request
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return {"error": "No Authorization header"}
    
    if not auth_header.startswith("Bearer "):
        return {"error": "Invalid Authorization format"}
    
    token = auth_header.split(" ")[1]
    
    try:
        # First, decode without verification to see payload
        unverified = jwt.decode(token, options={"verify_signature": False})
        print(f"Unverified payload: {unverified}")
        
        # Check expiration manually
        exp_timestamp = unverified.get('exp', 0)
        current_timestamp = datetime.now().timestamp()
        is_expired = exp_timestamp < current_timestamp
        
        result = {
            "unverified_payload": unverified,
            "expires_at": datetime.fromtimestamp(exp_timestamp).isoformat(),
            "current_time": datetime.fromtimestamp(current_timestamp).isoformat(),
            "is_expired": is_expired
        }
        
        # Try to decode with verification
        try:
            verified_payload = decode_access_token(token)
            result["verified_payload"] = verified_payload
            
            # Check if user exists
            user_id = verified_payload.get("user_id")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                result["user_exists"] = user is not None
                result["user_details"] = {
                    "id": user.id,
                    "email": user.email,
                    "username": getattr(user, 'username', 'N/A')
                } if user else None
            
        except Exception as decode_error:
            result["decode_error"] = str(decode_error)
            result["decode_error_type"] = type(decode_error).__name__
        
        return result
        
    except Exception as e:
        return {"error": str(e), "error_type": type(e).__name__}


@router.get("/test-user-lookup/{user_id}")
async def test_user_lookup(user_id: int, db: Session = Depends(get_db)):
    """Test if a specific user exists in database."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return {"error": f"User {user_id} not found"}
    
    return {
        "user_found": True,
        "user_id": user.id,
        "email": user.email,
        "username": getattr(user, 'username', 'N/A'),
        "created_at": getattr(user, 'created_at', 'N/A')
    }