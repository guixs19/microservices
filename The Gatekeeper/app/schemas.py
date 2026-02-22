from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    balance: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    type: str
    description: Optional[str]
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class PaymentSimulation(TransactionBase):
    pass

class PaymentResponse(BaseModel):
    success: bool
    message: str
    new_balance: float
    transaction_id: Optional[int] = None

class RechargeResponse(PaymentResponse):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None