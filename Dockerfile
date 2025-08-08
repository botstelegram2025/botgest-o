# Dockerfile Railway - CORREÇÃO DEFINITIVA externally-managed-environment
FROM node:20-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    python3-full \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Criar links simbólicos
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# Verificar versões
RUN echo "✅ Node.js: $(node --version)" && \
    echo "✅ NPM: $(npm --version)" && \
    echo "✅ Python: $(python3 --version)" && \
    echo "✅ Pip: $(pip3 --version)"

# Configurar diretório
WORKDIR /app

# Estratégia 1: Remover arquivo que ativa o erro
RUN rm -f /usr/lib/python*/EXTERNALLY-MANAGED 2>/dev/null || true

# Estratégia 2: Configurar pip para ignorar o erro globalmente
RUN mkdir -p /root/.config/pip && \
    echo "[global]\nbreak-system-packages = true" > /root/.config/pip/pip.conf

# Estratégia 3: Atualizar pip
RUN python3 -m pip install --upgrade pip --break-system-packages

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt

# Verificar instalação de pacotes Python
RUN python3 -c "import telegram; import psycopg2; import flask; print('✅ Pacotes Python instalados com sucesso!')"

# Instalar dependências Node.js
COPY baileys-server/package.json ./baileys-server/
WORKDIR /app/baileys-server
RUN npm install --production --no-optional

# Verificar instalação de pacotes Node.js
RUN node -e "console.log('✅ Baileys:', require('@whiskeysockets/baileys')); console.log('✅ Express:', require('express'));"

# Voltar ao diretório raiz da aplicação
WORKDIR /app
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/baileys-server/auth_info

# Configurar variáveis de ambiente
ENV PYTHONPATH=/app
ENV NODE_ENV=production
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expor as portas usadas
EXPOSE 5001
EXPOSE 3000

# Healthcheck robusto (testa ambos endpoints)
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:5000/health || curl -f http://localhost:5000/ || exit 1

# Comando padrão de inicialização
CMD ["python3", "start_railway.py"]
