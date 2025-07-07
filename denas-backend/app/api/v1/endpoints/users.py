from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.user import User, UserCreate
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user (in production, hash the password)
    db_user = UserModel(
        email=user.email,
        username=user.username,
        hashed_password=user.password,  # Hash this in production!
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user 