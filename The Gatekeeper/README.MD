# 💳 Sistema de Gerenciamento de Créditos

Um sistema completo para gerenciamento de créditos com FastAPI, SQLite e Docker. O sistema garante que o saldo do usuário nunca fique negativo!

## ✨ Funcionalidades

### 🎯 Principais
- ✅ **Saldo nunca negativo** - Sistema valida antes de cada débito
- ✅ **Autenticação JWT** - Segurança com tokens
- ✅ **Dashboard interativo** - Interface responsiva e moderna
- ✅ **Histórico de transações** - Registro completo com timestamps
- ✅ **Gráfico de gastos** - Visualização da evolução dos créditos
- ✅ **Exportação CSV** - Relatórios das transações

### 🚀 Extras
- Webhook simulado para pagamentos
- Recarga de créditos
- Feedback visual em tempo real
- Atualização automática do saldo

## 🛠️ Tecnologias

- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados:** SQLite
- **Autenticação:** JWT + Bcrypt
- **Container:** Docker & Docker Compose
- **Gráficos:** Chart.js

## 📋 Pré-requisitos

- Docker e Docker Compose (recomendado)
- OU Python 3.11+ e pip (para execução local)

## 🚀 Instalação e Execução

### 🐳 Com Docker (Recomendado)

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/sistema-creditos.git
cd sistema-creditos