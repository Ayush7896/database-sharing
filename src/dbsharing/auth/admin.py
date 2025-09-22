
from datetime import timedelta, timezone
import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from dbsharing.schemas.pydantic_models import UserVerification
from dbsharing.db.models import Users
from passlib.context import CryptContext
from dbsharing.db.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from dbsharing.auth.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

SECRET_KEY = "a2c4557a1531731c84059d83f4b552862dff447eec697e62ae40a1a5b0c6ef83"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/test",status_code=status.HTTP_200_OK)
async def test_endpoint(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    return db.query(Users).all()
    

@router.delete("/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    
    user_to_delete = db.query(Users).filter(Users.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user_to_delete)
    db.commit()
    return {"detail": "User deleted successfully"}


@router.put('/change_password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user_verification: UserVerification, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    current_user =  db.query(Users).filter(Users.id == user.get('user_id')).first()
    if not current_user:
        raise HTTPException(status_code=401, detail='User not found')
    if not bcrypt_context.verify(user_verification.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail='Wrong Password')
    current_user.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(current_user)
    db.commit()
    
    return {"detail": "Password changed successfully"}
