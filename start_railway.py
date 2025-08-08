#!/usr/bin/env python3
"""
Inicialização Railway: inicia API Baileys, bot Python e healthcheck Flask
"""

import os
import sys
import time
import subprocess
import threading
import signal
import logging
from flask import Flask

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Healthcheck Flask app ===
health_app = Flask(__name__)

@health_app.route("/health")
def health():
    return "ok", 200

def run_health_server():
    health_app.run(host="0.0.0.0", port=5001)

# === Railway Starter ===
class RailwayStarter:
    def __init__(self):
        self.baileys_process = None
        self.bot_process = None
        self.running = True

    def start_baileys_api(self):
        try:
            logger.info("🚀 Iniciando Baileys API...")
            os.chdir('/app/baileys-server')

            if not os.path.exists('package.json'):
                logger.error("❌ package.json não encontrado em baileys-server")
                return False

            self.baileys_process = subprocess.Popen(
                ['node', 'server.js'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("✅ Baileys API iniciada (PID: %d)", self.baileys_process.pid)
            return True
        except Exception as e:
            logger.error("❌ Erro ao iniciar Baileys API: %s", e)
            return False

    def start_bot(self):
        try:
            logger.info("🤖 Iniciando Bot Python...")
            os.chdir('/app')

            if not os.path.exists('bot_complete.py'):
                logger.error("❌ bot_complete.py não encontrado")
                return False

            os.environ['PYTHONPATH'] = '/app'
            os.environ['RAILWAY_ENVIRONMENT'] = 'production'

            self.bot_process = subprocess.Popen(
                [sys.executable, 'bot_complete.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("✅ Bot Python iniciado (PID: %d)", self.bot_process.pid)
            return True
        except Exception as e:
            logger.error("❌ Erro ao iniciar Bot: %s", e)
            return False

    def monitor_processes(self):
        while self.running:
            try:
                if self.baileys_process and self.baileys_process.poll() is not None:
                    logger.warning("⚠️ Baileys API parou. Reiniciando...")
                    self.start_baileys_api()

                if self.bot_process and self.bot_process.poll() is not None:
                    logger.warning("⚠️ Bot parou. Reiniciando...")
                    self.start_bot()

                time.sleep(30)
            except Exception as e:
                logger.error("❌ Erro no monitoramento: %s", e)
                time.sleep(10)

    def handle_signal(self, signum, frame):
        logger.info("🛑 Recebido sinal %d. Encerrando...", signum)
        self.running = False

        if self.baileys_process:
            self.baileys_process.terminate()
        if self.bot_process:
            self.bot_process.terminate()

        sys.exit(0)

    def start(self):
        logger.info("🚀 Iniciando sistema Railway...")

        # Sinais
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

        # Iniciar Flask /health em thread
        flask_thread = threading.Thread(target=run_health_server)
        flask_thread.daemon = True
        flask_thread.start()

        # Aguardar ambiente Railway
        time.sleep(5)

        # Iniciar serviços
        if not self.start_baileys_api():
            logger.error("❌ Falha ao iniciar Baileys API")
            return False

        time.sleep(10)

        if not self.start_bot():
            logger.error("❌ Falha ao iniciar Bot")
            return False

        logger.info("✅ Todos os serviços iniciados com sucesso!")

        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Loop principal
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.handle_signal(signal.SIGINT, None)

        return True

def main():
    try:
        starter = RailwayStarter()
        if not starter.start():
            logger.error("❌ Sistema não iniciou corretamente")
            sys.exit(1)
    except Exception as e:
        logger.error("❌ Erro crítico: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
