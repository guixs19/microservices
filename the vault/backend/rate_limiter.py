import time
from datetime import datetime, timedelta, timezone  # Adicionado timezone
from typing import Dict, Tuple
from sqlalchemy.orm import Session
from models import FailedLoginAttempt
from config import settings

class RateLimiter:
    def __init__(self):
        self.attempts: Dict[str, Dict[str, Tuple[int, float]]] = {}
    
    def check_login_attempt(self, db: Session, username: str, ip_address: str) -> Tuple[bool, str]:
        """
        Verifica se o login pode ser realizado
        
        Retorna: (pode_logar, mensagem)
        """
        # Registrar tentativa
        failed_attempt = FailedLoginAttempt(
            username=username,
            ip_address=ip_address
        )
        db.add(failed_attempt)
        db.commit()
        
        # Verificar tentativas recentes
        timeframe = datetime.now(timezone.utc) - timedelta(minutes=settings.LOGIN_TIMEFRAME_MINUTES)
        
        user_attempts = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username,
            FailedLoginAttempt.attempted_at >= timeframe
        ).count()
        
        ip_attempts = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.ip_address == ip_address,
            FailedLoginAttempt.attempted_at >= timeframe
        ).count()
        
        # Verificar bloqueio
        if user_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            block_time = datetime.now(timezone.utc) - timedelta(minutes=settings.BLOCK_DURATION_MINUTES)
            last_attempt = db.query(FailedLoginAttempt).filter(
                FailedLoginAttempt.username == username
            ).order_by(FailedLoginAttempt.attempted_at.desc()).first()
            
            if last_attempt and last_attempt.attempted_at > block_time:
                time_left = last_attempt.attempted_at + timedelta(minutes=settings.BLOCK_DURATION_MINUTES) - datetime.now(timezone.utc)
                minutes_left = int(time_left.total_seconds() / 60)
                return False, f"Conta bloqueada. Tente novamente em {minutes_left} minutos."
        
        if ip_attempts >= settings.MAX_LOGIN_ATTEMPTS * 2:
            return False, "Muitas tentativas deste IP. Tente novamente mais tarde."
        
        return True, "OK"
    
    def clear_successful_login(self, db: Session, username: str, ip_address: str):
        """Limpa tentativas falhas após login bem-sucedido"""
        db.query(FailedLoginAttempt).filter(
            (FailedLoginAttempt.username == username) |
            (FailedLoginAttempt.ip_address == ip_address)
        ).delete()
        db.commit()

rate_limiter = RateLimiter()