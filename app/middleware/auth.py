# Fixed middleware.py
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.auth import decode_access_token
from app.database import SessionLocal, get_db
from app.models.user import User


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware that validates JWT tokens for protected routes.
    """
    # Skip authentication for public routes
    public_routes = ["/login", "/register", "/docs", "/openapi.json", "/redoc"]
    if request.url.path in public_routes:
        response = await call_next(request)
        return response

    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401, 
            content={"error": "Missing or invalid authorization header"}
        )

    # Extract and validate token
    token = auth_header.split(" ")[1]
    db = None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=401, 
                content={"error": "Invalid token payload"}
            )

        # Get user from database
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return JSONResponse(
                status_code=401, 
                content={"error": "User not found"}
            )
        
        # Attach user to request state
        request.state.user = user
        
    except Exception as e:
        print(f"Auth error: {e}")  # For debugging
        return JSONResponse(
            status_code=401, 
            content={"error": "Invalid or expired token"}
        )
    finally:
        if db:
            db.close()

    response = await call_next(request)
    return response


# Alternative: Dependency-based authentication (recommended)
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    Use this instead of middleware if you prefer dependency injection.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = auth_header.split(" ")[1]
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")