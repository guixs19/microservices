from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone  # Adicionado timezone
import models
import auth
from database import engine, get_db
from config import settings
from rate_limiter import rate_limiter

# Criar tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="The Vault API",
    description="Sistema seguro de autenticação com Argon2 e JWT",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
@app.post("/api/register", response_model=auth.AuthResponse)
async def register(
    user_data: auth.UserCreate,
    db: Session = Depends(get_db)
):
    """Registra um novo usuário"""
    # Verificar se usuário já existe
    existing_user = db.query(models.User).filter(
        (models.User.username == user_data.username) |
        (models.User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username ou email já cadastrado"
        )
    
    # Criar usuário
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Gerar token
    access_token = auth.create_access_token(
        data={"sub": db_user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return auth.AuthResponse(
        success=True,
        message="Usuário registrado com sucesso",
        token=auth.Token(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        user=auth.UserBase(
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name
        )
    )

@app.post("/api/login", response_model=auth.AuthResponse)
async def login(
    request: Request,
    login_data: auth.UserLogin,
    db: Session = Depends(get_db)
):
    """Realiza login do usuário"""
    # Verificar rate limiting
    can_login, message = rate_limiter.check_login_attempt(
        db, login_data.username, request.client.host
    )
    
    if not can_login:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message
        )
    
    # Autenticar usuário
    user = auth.authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Limpar tentativas falhas
    rate_limiter.clear_successful_login(db, login_data.username, request.client.host)
    
    # Atualizar último login - CORRIGIDO
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Gerar token
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return auth.AuthResponse(
        success=True,
        message="Login realizado com sucesso",
        token=auth.Token(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        user=auth.UserBase(
            username=user.username,
            email=user.email,
            full_name=user.full_name
        )
    )

@app.get("/api/profile", response_model=auth.UserBase)
async def get_profile(
    current_user: models.User = Depends(auth.get_current_user)
):
    """Retorna perfil do usuário autenticado"""
    return auth.UserBase(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name
    )

@app.get("/api/health")
async def health_check():
    """Endpoint de saúde da API"""
    return {"status": "healthy", "service": "The Vault API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)