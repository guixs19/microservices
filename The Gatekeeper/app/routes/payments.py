from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.auth import get_current_active_user


router = APIRouter(tags=["payments"])

@router.post("/simulate", response_model=schemas.PaymentResponse)
def simulate_payment(
    payment: schemas.PaymentSimulation,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_active_user)
):
    transaction, message = crud.process_payment(db, current_user.id, payment)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return schemas.PaymentResponse(
        success=True,
        message=message,
        new_balance=current_user.balance - payment.amount,
        transaction_id=transaction.id
    )

@router.post("/recharge", response_model=schemas.RechargeResponse)
def recharge_credits(
    recharge: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_active_user)
):
    transaction = crud.process_recharge(db, current_user.id, recharge)
    
    return schemas.RechargeResponse(
        success=True,
        message="Recarga realizada com sucesso",
        new_balance=current_user.balance + recharge.amount,
        transaction_id=transaction.id
    )

@router.post("/webhook/payment-confirmation")
def payment_webhook(webhook_data: dict):
    return {"status": "received", "data": webhook_data}