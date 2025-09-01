from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from passlib.context import CryptContext

# Make sure these match your actual values
SECRET_KEY = "your-secret-key-here"  # IMPORTANT: Use the same key for encoding/decoding
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"🎫 Created token with payload: {to_encode}")
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Token decoded successfully: {payload}")
        return payload
        
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error decoding token: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)