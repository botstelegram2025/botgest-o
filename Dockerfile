# Dockerfile.railway - Node.js 20 + Python 3.11 com venv
FROM node:20-slim

# Instalar Python e dependências
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Criar symlinks
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3

# Configurar diretório
WORKDIR /app

# Criar ambiente virtual
RUN python3 -m venv /opt/venv

# Ativar ambiente virtual permanentemente
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements e instalar usando pip do venv
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código restante
COPY . .

# Instalar dependências do Node.js
WORKDIR /app/baileys-server
RUN npm install

# Voltar ao diretório principal
WORKDIR /app

# Criar diretórios necessários
RUN mkdir -p /app/baileys-server/auth_info

# Configurar ambiente
ENV PYTHONPATH=/app
ENV NODE_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expor portas
EXPOSE 5000
EXPOSE 3000

# Healthcheck para Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicialização
CMD ["python", "start_railway.py"]
