#!/usr/bin/env python3
"""
Arquivo de inicialização para Railway
Inicia tanto a API Baileys quanto o bot Python
"""

import os
import sys
import time
import subprocess
import threading
import signal
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RailwayStarter:
    def __init__(self):
        self.baileys_process = None
        self.bot_process = None
        self.running = True
        
    def start_baileys_api(self):
        """Inicia a API Baileys em background"""
        try:
            logger.info("🚀 Iniciando Baileys API...")
            os.chdir('/app/baileys-server')
            
            # Verificar se package.json existe
            if not os.path.exists('package.json'):
                logger.error("❌ package.json não encontrado em baileys-server")
                return False
                
            # Iniciar servidor Node.js
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
        """Inicia o bot Python"""
        try:
            logger.info("🤖 Iniciando Bot Python...")
            os.chdir('/app')
            
            # Verificar se arquivo principal existe
            if not os.path.exists('bot_complete.py'):
                logger.error("❌ bot_complete.py não encontrado")
                return False
            
            # Configurar variáveis de ambiente para Railway
            os.environ['PYTHONPATH'] = '/app'
            os.environ['RAILWAY_ENVIRONMENT'] = 'production'
            
            # Iniciar bot
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
        """Monitora os processos e reinicia se necessário"""
        while self.running:
            try:
                # Verificar Baileys API
                if self.baileys_process and self.baileys_process.poll() is not None:
                    logger.warning("⚠️ Baileys API parou. Reiniciando...")
                    self.start_baileys_api()
                
                # Verificar Bot
                if self.bot_process and self.bot_process.poll() is not None:
                    logger.warning("⚠️ Bot parou. Reiniciando...")
                    self.start_bot()
                
                time.sleep(30)  # Verificar a cada 30 segundos
                
            except Exception as e:
                logger.error("❌ Erro no monitoramento: %s", e)
                time.sleep(10)
    
    def handle_signal(self, signum, frame):
        """Manipula sinais de parada"""
        logger.info("🛑 Recebido sinal %d. Parando serviços...", signum)
        self.running = False
        
        if self.baileys_process:
            self.baileys_process.terminate()
        
        if self.bot_process:
            self.bot_process.terminate()
        
        sys.exit(0)
    
    def start(self):
        """Inicia todos os serviços"""
        logger.info("🚀 Iniciando sistema no Railway...")
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        
        # Aguardar um pouco para Railway configurar ambiente
        time.sleep(5)
        
        # Iniciar Baileys API
        if not self.start_baileys_api():
            logger.error("❌ Falha ao iniciar Baileys API")
            return False
        
        # Aguardar API inicializar
        time.sleep(10)
        
        # Iniciar Bot
        if not self.start_bot():
            logger.error("❌ Falha ao iniciar Bot")
            return False
        
        logger.info("✅ Todos os serviços iniciados com sucesso!")
        
        # Iniciar monitoramento em thread separada
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Manter processo principal ativo
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.handle_signal(signal.SIGINT, None)
        
        return True

def main():
    """Função principal"""
    try:
        starter = RailwayStarter()
        success = starter.start()
        
        if not success:
            logger.error("❌ Falha ao iniciar sistema")
            sys.exit(1)
            
    except Exception as e:
        logger.error("❌ Erro crítico: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()