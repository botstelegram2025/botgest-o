FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia o projeto
COPY . /app

# Variáveis úteis
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependências Python
RUN pip install --no-cache-dir \
    python-telegram-bot \
    psycopg2-binary \
    apscheduler \
    pytz \
    qrcode \
    pillow \
    requests \
    python-dotenv \
    flask \
    gunicorn

# Porta da aplicação (ajuste se necessário)
EXPOSE 5000

# Inicia a aplicação
# Se seu app for Flask com `app` em main.py, você pode usar gunicorn:
# CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]

# Caso contrário, executa diretamente o main.py
CMD ["python", "main.py"]
