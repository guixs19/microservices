# 🔐 The Vault - Sistema de Autenticação Seguro

> Sistema completo de cadastro e login com foco em segurança, implementando Argon2id, JWT e proteção contra brute force.

## ✨ Destaques Técnicos

### 🛡️ Segurança
- **Argon2id** para hashing de senhas (vencedor do Password Hashing Competition)
- **Tokens JWT** com expiração de 30 minutos
- **Rate Limiting** contra ataques de força bruta (5 tentativas/15min)
- **Validação rigorosa** de inputs

### 🏗️ Arquitetura
- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: HTML/CSS/JS puro
- **Banco**: SQLite com ORM
- **API RESTful** com documentação automática

## 🚀 Como Executar

### Backend:
```bash
cd backend
pip install -r requirements.txt
python main.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs