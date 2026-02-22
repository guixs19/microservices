from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db
from app.auth import get_current_active_user


router = APIRouter(tags=["users"])

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = crud.get_user_by_email(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(get_current_active_user)):
    return current_user

@router.get("/balance", response_model=float)
def get_balance(current_user: schemas.UserResponse = Depends(get_current_active_user)):
    return current_user.balance

@router.get("/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_active_user)
):
    transactions = crud.get_user_transactions(db, user_id=current_user.id, skip=skip, limit=limit)
    return transactions