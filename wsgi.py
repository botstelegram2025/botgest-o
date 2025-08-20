# wsgi.py - ponto de entrada WSGI para servidores como Gunicorn
from app import app

# Expõe 'app' para o servidor WSGI
__all__ = ["app"]
