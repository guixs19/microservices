# Imagem base oficial do Python
FROM python:3.11-slim

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# Instalar dependências do sistema (caso necessário)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de requisitos primeiro (para aproveitar cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto da aplicação
COPY . .

# Criar diretório para o banco de dados SQLite
RUN mkdir -p /app/data && chmod 777 /app/data

# Expor porta da aplicação
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]