# Dockerfile otimizado para Railway com Node.js 20
FROM python:3.11-slim

# Instalar Node.js 20 e dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js 20 via NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verificar versões instaladas
RUN node --version && npm --version

# Definir diretório de trabalho
WORKDIR /app

# Copiar todos os arquivos primeiro
COPY . .

# Instalar dependências Python
RUN pip install --no-cache-dir \
    python-telegram-bot==20.7 \
    psycopg2-binary>=2.9.10 \
    APScheduler>=3.11.0 \
    pytz>=2025.2 \
    qrcode>=8.2 \
    Pillow>=11.3.0 \
    requests>=2.32.4 \
    python-dotenv>=1.1.1 \
    Flask>=3.1.1 \
    gunicorn>=23.0.0

# Verificar se package.json existe e instalar dependências Node.js
RUN if [ -f "/app/baileys-server/package.json" ]; then \
        cd /app/baileys-server && npm install; \
    else \
        echo "package.json não encontrado em baileys-server"; \
        exit 1; \
    fi

# Criar diretório para autenticação WhatsApp
RUN mkdir -p /app/baileys-server/auth_info

# Dar permissões necessárias
RUN chmod +x /app/start_railway.py 2>/dev/null || true

# Expor portas
EXPOSE 5001 3000

# Health check simples
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Comando para iniciar aplicação
CMD ["python3", "start_railway.py"]