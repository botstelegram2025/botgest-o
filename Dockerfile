# Dockerfile Railway - Versão Final 100% Funcional
FROM node:20-slim

# Instalar Python 3.11 e dependências essenciais
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python

# Verificar instalações
RUN echo "Node.js:" && node --version && \
    echo "NPM:" && npm --version && \
    echo "Python:" && python3 --version && \
    echo "Pip:" && pip3 --version

# Configurar diretório
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copiar baileys-server e instalar dependências Node.js  
COPY baileys-server/ ./baileys-server/
WORKDIR /app/baileys-server
RUN npm install --production

# Voltar para diretório principal e copiar arquivos
WORKDIR /app
COPY . .

# Criar diretório auth
RUN mkdir -p /app/baileys-server/auth_info

# Configurar ambiente
ENV PYTHONPATH=/app
ENV NODE_ENV=production

# Portas
EXPOSE 5000
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando final
CMD ["python3", "start_railway.py"]