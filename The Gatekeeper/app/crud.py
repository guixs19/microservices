"""
Módulo de operações CRUD para o banco de dados
Gerencia usuários, transações e operações de crédito
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime
from typing import Optional, List


from app import models, schemas
from passlib.context import CryptContext

# Configuração de hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================
# UTILITÁRIOS
# ============================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

# ============================================
# CRUD DE USUÁRIOS
# ============================================

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Busca usuário por ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Busca usuário por nome de usuário"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Busca usuário por email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Lista todos os usuários"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Cria um novo usuário
    - Verifica se usuário/email já existe
    - Hash da senha antes de salvar
    """
    # Verificar se já existe
    if get_user_by_username(db, user.username):
        raise ValueError("Username already registered")
    if get_user_by_email(db, user.email):
        raise ValueError("Email already registered")
    
    # Criar usuário
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        balance=0.0  # Saldo inicial zero
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Criar transação de boas-vindas (opcional)
    welcome_transaction = models.Transaction(
        user_id=db_user.id,
        amount=0.0,
        type="credit",
        description="Bem-vindo ao sistema de créditos!",
        status="completed"
    )
    db.add(welcome_transaction)
    db.commit()
    
    return db_user

def update_user(db: Session, user_id: int, user_update: dict) -> Optional[models.User]:
    """Atualiza dados do usuário"""
    user = get_user(db, user_id)
    if user:
        for key, value in user_update.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """Remove um usuário"""
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def authenticate_user(db: Session, username: str, password: str):
    """
    Autentica um usuário
    Retorna o usuário se credenciais válidas, False caso contrário
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# ============================================
# CRUD DE TRANSAÇÕES
# ============================================

def create_transaction(
    db: Session, 
    user_id: int, 
    amount: float, 
    transaction_type: str, 
    description: Optional[str] = None,
    status: str = "completed"
) -> models.Transaction:
    """
    Cria uma nova transação
    - transaction_type: 'credit' (entrada) ou 'debit' (saída)
    """
    db_transaction = models.Transaction(
        user_id=user_id,
        amount=amount,
        type=transaction_type,
        description=description,
        status=status
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_user_transactions(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    transaction_type: Optional[str] = None
) -> List[models.Transaction]:
    """
    Retorna transações do usuário
    - Opção de filtrar por tipo (credit/debit)
    - Ordenado por data (mais recente primeiro)
    """
    query = db.query(models.Transaction).filter(models.Transaction.user_id == user_id)
    
    if transaction_type:
        query = query.filter(models.Transaction.type == transaction_type)
    
    return query.order_by(desc(models.Transaction.timestamp)).offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    """Busca transação por ID"""
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def get_user_balance(db: Session, user_id: int) -> float:
    """Retorna o saldo atual do usuário"""
    user = get_user(db, user_id)
    return user.balance if user else 0.0

# ============================================
# OPERAÇÕES DE CRÉDITO (COM VALIDAÇÃO DE SALDO)
# ============================================

def check_sufficient_balance(db: Session, user_id: int, amount: float) -> bool:
    """
    Verifica se o usuário tem saldo suficiente
    - Retorna True se saldo >= amount
    - Retorna False caso contrário
    """
    user = get_user(db, user_id)
    return user and user.balance >= amount

def process_payment(db: Session, user_id: int, payment: schemas.PaymentSimulation):
    """
    Processa um pagamento (débito)
    - Verifica saldo suficiente
    - Atualiza saldo do usuário
    - Registra transação
    - Retorna (transaction, message)
    """
    # Verificar saldo suficiente
    if not check_sufficient_balance(db, user_id, payment.amount):
        return None, "Saldo insuficiente para realizar o pagamento"
    
    user = get_user(db, user_id)
    
    # Atualizar saldo (NUNCA fica negativo graças à verificação acima)
    user.balance -= payment.amount
    
    # Registrar transação
    transaction = create_transaction(
        db=db,
        user_id=user_id,
        amount=payment.amount,
        transaction_type="debit",
        description=payment.description or "Pagamento realizado"
    )
    
    db.commit()
    db.refresh(user)
    
    return transaction, "Pagamento realizado com sucesso"

def process_recharge(db: Session, user_id: int, recharge: schemas.TransactionCreate):
    """
    Processa uma recarga (crédito)
    - Adiciona créditos ao saldo
    - Registra transação
    """
    user = get_user(db, user_id)
    
    # Adicionar créditos
    user.balance += recharge.amount
    
    # Registrar transação
    transaction = create_transaction(
        db=db,
        user_id=user_id,
        amount=recharge.amount,
        transaction_type="credit",
        description=recharge.description or "Recarga de créditos"
    )
    
    db.commit()
    db.refresh(user)
    
    return transaction

# ============================================
# ESTATÍSTICAS E RELATÓRIOS
# ============================================

def get_transaction_stats(db: Session, user_id: int, days: int = 30):
    """
    Retorna estatísticas das transações dos últimos N dias
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    transactions = db.query(models.Transaction).filter(
        and_(
            models.Transaction.user_id == user_id,
            models.Transaction.timestamp >= cutoff_date
        )
    ).all()
    
    total_credits = sum(t.amount for t in transactions if t.type == "credit")
    total_debits = sum(t.amount for t in transactions if t.type == "debit")
    
    return {
        "total_transactions": len(transactions),
        "total_credits": total_credits,
        "total_debits": total_debits,
        "net_change": total_credits - total_debits,
        "period_days": days
    }

def get_daily_summary(db: Session, user_id: int, days: int = 7):
    """
    Retorna resumo diário de transações para o gráfico
    """
    from datetime import timedelta, date
    
    summary = []
    for i in range(days):
        day = date.today() - timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        day_transactions = db.query(models.Transaction).filter(
            and_(
                models.Transaction.user_id == user_id,
                models.Transaction.timestamp >= day,
                models.Transaction.timestamp < next_day,
                models.Transaction.type == "debit"
            )
        ).all()
        
        total = sum(t.amount for t in day_transactions)
        
        summary.append({
            "date": day.strftime("%d/%m/%Y"),
            "total": total
        })
    
    return list(reversed(summary))  # Mais antigo primeiro