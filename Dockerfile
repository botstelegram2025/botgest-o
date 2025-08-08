# Dockerfile - Base Node.js 20 com Python
FROM node:20-slim

RUN echo "🔍 Node.js na imagem base:" && \
    node --version && \
    npm --version && \
    echo "✅ Node.js 20 confirmado!"

# Instalar Python 3.11 e dependências
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    echo "🔍 Python instalado:" && \
    python3 --version && \
    pip3 --version

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos
COPY . .

# Instalar dependências Python (com correções)
RUN pip3 install --no-cache-dir --break-system-packages \
    python-telegram-bot==20.7 \
    psycopg2-binary>=2.9.10 \
    APScheduler>=3.11.0 \
    pytz>=2024.1 \
    qrcode>=8.2 \
    Pillow>=11.3.0 \
    requests>=2.32.4 \
    python-dotenv>=1.1.1 \
    Flask>=3.1.1 \
    gunicorn>=23.0.0

# Instalar dependências Node.js do baileys
RUN if [ -f "/app/baileys-server/package.json" ]; then \
        cd /app/baileys-server && \
        echo "📦 Instalando dependências do Baileys com Node.js $(node --version)..." && \
        echo "🔍 Verificando npm:" && \
        which npm && \
        npm --version && \
        npm install --verbose && \
        echo "✅ Dependências do Baileys instaladas com sucesso!"; \
    else \
        echo "❌ package.json não encontrado em baileys-server"; \
        exit 1; \
    fi

# Diretório para sessões WhatsApp
RUN mkdir -p /app/baileys-server/auth_info

# Permissões
RUN chmod +x /app/start_railway.py 2>/dev/null || true

# Expor portas
EXPOSE 5001 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Start
CMD ["python3", "start_railway.py"]
