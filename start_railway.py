#!/usr/bin/env python3
"""
Railway Starter - VERSÃO CORRIGIDA FINAL
Resolve definitivamente o problema externally-managed-environment
"""

import os
import sys
import time
import subprocess
import threading
import signal
import logging
from flask import Flask, jsonify

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask app para Railway
app = Flask(__name__)

# Global state
baileys_process = None
bot_thread = None
running = True

@app.route('/health')
def health():
    """Health check obrigatório para Railway"""
    global baileys_process, bot_thread
    
    baileys_ok = baileys_process is not None and baileys_process.poll() is None
    bot_ok = bot_thread is not None and bot_thread.is_alive()
    
    status = "healthy" if (baileys_ok and bot_ok) else "starting"
    
    return jsonify({
        "status": status,
        "service": "Bot Gestão Clientes Railway",
        "components": {
            "baileys_api": "running" if baileys_ok else "stopped",
            "telegram_bot": "running" if bot_ok else "stopped",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "node_available": os.path.exists("/usr/local/bin/node")
        },
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC')
    }), 200

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Bot Gestão Clientes",
        "status": "operational", 
        "version": "1.0.0-railway-fixed",
        "endpoints": ["/health", "/"],
        "baileys_api": "http://localhost:3000",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC')
    })

def start_baileys_api():
    """Inicia API Baileys"""
    global baileys_process
    
    try:
        logger.info("🚀 Iniciando Baileys API...")
        
        # Mudar para diretório baileys
        baileys_dir = '/app/baileys-server'
        if not os.path.exists(baileys_dir):
            logger.error(f"❌ Diretório não encontrado: {baileys_dir}")
            return False
            
        os.chdir(baileys_dir)
        
        # Verificar arquivos necessários
        if not os.path.exists('server.js'):
            logger.error("❌ server.js não encontrado")
            return False
            
        if not os.path.exists('package.json'):
            logger.error("❌ package.json não encontrado") 
            return False
        
        # Iniciar processo Node.js
        baileys_process = subprocess.Popen(
            ['node', 'server.js'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        logger.info(f"✅ Baileys API iniciada (PID: {baileys_process.pid})")
        
        # Thread para logs do Baileys
        def log_baileys_output():
            while baileys_process and baileys_process.poll() is None:
                try:
                    line = baileys_process.stdout.readline()
                    if line:
                        logger.info(f"[Baileys] {line.strip()}")
                except:
                    break
        
        threading.Thread(target=log_baileys_output, daemon=True).start()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar Baileys: {e}")
        return False

def start_telegram_bot():
    """Inicia bot Telegram"""
    try:
        logger.info("🤖 Iniciando Bot Telegram...")
        
        # Voltar para diretório principal
        os.chdir('/app')
        
        # Configurar ambiente Python
        os.environ['PYTHONPATH'] = '/app'
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        
        # Verificar variáveis obrigatórias
        bot_token = os.getenv('BOT_TOKEN')
        admin_chat_id = os.getenv('ADMIN_CHAT_ID')
        
        if not bot_token:
            logger.error("❌ BOT_TOKEN não configurado!")
            return
            
        if not admin_chat_id:
            logger.error("❌ ADMIN_CHAT_ID não configurado!")
            return
        
        # Importar e inicializar bot
        from bot_complete import TelegramBot
        
        bot = TelegramBot(bot_token)
        
        # Inicializar serviços
        if not bot.initialize_services():
            logger.error("❌ Falha ao inicializar serviços do bot")
            return
        
        logger.info("✅ Bot Telegram inicializado!")
        
        # Loop de polling
        import requests
        
        offset = None
        consecutive_errors = 0
        
        while running:
            try:
                # Fazer long polling
                url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
                params = {
                    'timeout': 30,
                    'limit': 100
                }
                
                if offset:
                    params['offset'] = offset
                
                response = requests.get(url, params=params, timeout=35)
                
                if response.status_code == 200:
                    consecutive_errors = 0
                    data = response.json()
                    
                    if data.get('ok') and data.get('result'):
                        for update in data['result']:
                            try:
                                bot.process_message(update)
                                offset = update['update_id'] + 1
                            except Exception as e:
                                logger.error(f"Erro ao processar update: {e}")
                else:
                    consecutive_errors += 1
                    logger.warning(f"Telegram API error {response.status_code} (#{consecutive_errors})")
                    
                    if consecutive_errors >= 5:
                        logger.error("Muitos erros consecutivos, pausando...")
                        time.sleep(30)
                        consecutive_errors = 0
                    else:
                        time.sleep(5)
                        
            except requests.Timeout:
                # Timeout é normal no long polling
                continue
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Erro no polling #{consecutive_errors}: {e}")
                time.sleep(10 if consecutive_errors < 3 else 30)
                
    except Exception as e:
        logger.error(f"❌ Erro crítico no bot: {e}")

def handle_shutdown(signum, frame):
    """Handle graceful shutdown"""
    global running, baileys_process
    
    logger.info(f"🛑 Shutdown signal {signum} received")
    running = False
    
    if baileys_process:
        logger.info("Parando Baileys API...")
        baileys_process.terminate()
        
        # Aguardar processo terminar
        try:
            baileys_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            logger.warning("Forçando parada do Baileys...")
            baileys_process.kill()
    
    logger.info("✅ Shutdown concluído")
    sys.exit(0)

def main():
    """Função principal"""
    global bot_thread
    
    logger.info("🚀 Iniciando sistema Railway (versão corrigida)...")
    
    # Configurar handlers de sinal
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    # Aguardar Railway configurar ambiente
    logger.info("⏳ Aguardando inicialização Railway...")
    time.sleep(3)
    
    # Iniciar Baileys API
    logger.info("📱 Configurando Baileys API...")
    if not start_baileys_api():
        logger.error("❌ Falha crítica ao iniciar Baileys API")
        return
    
    # Aguardar Baileys inicializar
    time.sleep(5)
    
    # Iniciar bot em thread separada
    logger.info("🤖 Configurando Bot Telegram...")
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Aguardar bot inicializar
    time.sleep(3)
    
    logger.info("✅ Todos os serviços configurados!")
    logger.info("🌐 Iniciando servidor Flask na porta 5000...")
    
    # Iniciar servidor Flask (blocking)
    try:
        app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        handle_shutdown(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"❌ Erro no servidor Flask: {e}")
        handle_shutdown(signal.SIGTERM, None)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupção por teclado recebida (CTRL+C)")
        handle_shutdown(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}", exc_info=True)
        handle_shutdown(signal.SIGTERM, None)

