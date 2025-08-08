# Dockerfile.railway - Corrigido para Railway (Python + Node.js)
FROM node:20-slim

# Instalar Python e dependências
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-full \
    python3-pip \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Symlinks para comandos python/pip padrão
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Desbloquear instalação via pip (PEP 668)
RUN rm -f /usr/lib/python*/EXTERNALLY-MANAGED || true

# Configurar pip para ignorar PEP 668
RUN mkdir -p /root/.config/pip && \
    echo "[global]" >> /root/.config/pip/pip.conf && \
    echo "break-system-packages = true" >> /root/.config/pip/pip.conf

# Atualizar pip
RUN python3 -m pip install --upgrade pip --break-system-packages

# Diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copiar dependências Node.js do baileys
COPY baileys-server/package.json ./baileys-server/
WORKDIR /app/baileys-server
RUN npm install --production --no-optional

# Verificações (opcional)
RUN node -e "console.log('✅ Baileys:', require('@whiskeysockets/baileys'))"

# Copiar todo o restante do projeto
WORKDIR /app
COPY . .

# Criar diretórios obrigatórios
RUN mkdir -p /app/baileys-server/auth_info

# Definir variáveis de ambiente
ENV PYTHONPATH=/app
ENV NODE_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Expor portas
EXPOSE 5000
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Iniciar app principal
CMD ["python3", "start_railway.py"]
