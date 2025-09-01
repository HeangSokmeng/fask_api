from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_password
from app.database import SessionLocal
from app.models.user import User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


from app.auth.auth import get_password_hash

new_user = User(
    name="Ant",
    email="ant@example.com",
    password=get_password_hash("123456")  # hash before saving
)
db.add(new_user)
db.commit()
