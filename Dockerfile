# Dockerfile com instalação robusta do Node.js 20
FROM node:20-slim as node-stage

# Verificar versão do Node.js na imagem base
RUN node --version && npm --version

# Usar Python como base principal e copiar Node.js
FROM python:3.11-slim

# Copiar Node.js da imagem anterior
COPY --from=node-stage /usr/local/bin/node /usr/local/bin/
COPY --from=node-stage /usr/local/bin/npm /usr/local/bin/
COPY --from=node-stage /usr/local/bin/npx /usr/local/bin/
COPY --from=node-stage /usr/local/include/node /usr/local/include/node
COPY --from=node-stage /usr/local/lib/node_modules /usr/local/lib/node_modules

# Criar link simbólico para compatibilidade
RUN ln -sf /usr/local/bin/node /usr/bin/node && \
    ln -sf /usr/local/bin/npm /usr/bin/npm && \
    ln -sf /usr/local/bin/npx /usr/bin/npx

# Verificar se Node.js 20 foi instalado corretamente
RUN echo "🔍 Verificando Node.js instalado:" && \
    node --version && \
    npm --version && \
    node --version | grep -E "v20\." && \
    echo "✅ Node.js 20 instalado com sucesso!"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar todos os arquivos
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

# Verificar e instalar dependências Node.js com verificação robusta
RUN if [ -f "/app/baileys-server/package.json" ]; then \
        cd /app/baileys-server && \
        echo "🔍 Verificando Node.js antes do npm install..." && \
        which node && \
        node --version && \
        npm --version && \
        echo "📦 Iniciando instalação das dependências do Baileys..." && \
        npm install --verbose && \
        echo "✅ Dependências do Baileys instaladas com sucesso!"; \
    else \
        echo "❌ package.json não encontrado em baileys-server"; \
        exit 1; \
    fi

# Criar diretório para autenticação WhatsApp
RUN mkdir -p /app/baileys-server/auth_info

# Dar permissões necessárias
RUN chmod +x /app/start_railway.py 2>/dev/null || true

# Expor portas
EXPOSE 5001 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Comando para iniciar aplicação
CMD ["python3", "start_railway.py"]