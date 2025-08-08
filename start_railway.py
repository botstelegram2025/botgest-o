#!/usr/bin/env python3
"""
Inicializador Railway - Versão Final Simplificada
Inicia Baileys API e Bot de forma robusta
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

# Flask app para health check
app = Flask(__name__)

# Global processes
baileys_process = None
bot_thread = None
running = True

@app.route('/health')
def health():
    """Health check endpoint para Railway"""
    return jsonify({
        "status": "healthy",
        "service": "Bot Gestão Clientes Railway",
        "baileys": baileys_process is not None and baileys_process.poll() is None,
        "bot": bot_thread is not None and bot_thread.is_alive(),
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Bot Gestão Clientes",
        "status": "running",
        "version": "1.0.0-railway",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    })

def start_baileys():
    """Inicia Baileys API"""
    global baileys_process
    try:
        logger.info("🚀 Iniciando Baileys API...")
        os.chdir('/app/baileys-server')
        
        baileys_process = subprocess.Popen(
            ['node', 'server.js'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        logger.info(f"✅ Baileys API iniciada (PID: {baileys_process.pid})")
        
        # Log baileys output em thread separada
        def log_baileys():
            while baileys_process and baileys_process.poll() is None:
                output = baileys_process.stdout.readline()
                if output:
                    logger.info(f"[Baileys] {output.strip()}")
        
        threading.Thread(target=log_baileys, daemon=True).start()
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar Baileys: {e}")

def start_bot():
    """Inicia bot em thread"""
    try:
        logger.info("🤖 Iniciando Bot...")
        os.chdir('/app')
        
        # Importar e rodar bot
        from bot_complete import TelegramBot, BOT_TOKEN
        
        bot = TelegramBot(BOT_TOKEN)
        
        # Inicializar serviços
        if not bot.initialize_services():
            logger.error("❌ Falha ao inicializar serviços do bot")
            return
        
        logger.info("✅ Bot inicializado com sucesso!")
        
        # Polling loop
        import requests
        import json
        
        offset = None
        while running:
            try:
                # Get updates
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
                params = {'timeout': 30}
                if offset:
                    params['offset'] = offset
                
                response = requests.get(url, params=params, timeout=35)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok') and data.get('result'):
                        for update in data['result']:
                            bot.process_message(update)
                            offset = update['update_id'] + 1
                else:
                    logger.warning(f"Telegram API error: {response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                logger.error(f"Erro no bot polling: {e}")
                time.sleep(10)
                
    except Exception as e:
        logger.error(f"❌ Erro crítico no bot: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global running, baileys_process
    logger.info(f"🛑 Shutdown signal {signum} received")
    running = False
    
    if baileys_process:
        baileys_process.terminate()
    
    sys.exit(0)

def main():
    """Função principal"""
    global bot_thread
    
    logger.info("🚀 Iniciando sistema Railway...")
    
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start Baileys API
    start_baileys()
    time.sleep(5)  # Wait for Baileys to start
    
    # Start bot in thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    logger.info("✅ Todos os serviços iniciados!")
    
    # Start Flask server (blocking)
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()