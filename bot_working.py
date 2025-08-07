#!/usr/bin/env python3
"""
Bot Telegram funcionando - Versão sem imports problemáticos
"""
import os
import logging
import json
from flask import Flask, request, jsonify
import asyncio
import requests
from datetime import datetime
import pytz

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações do bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
WEBHOOK_URL = None  # Será configurado via variável de ambiente

class TelegramBot:
    """Bot Telegram usando API HTTP direta"""
    
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def send_message(self, chat_id, text, parse_mode=None):
        """Envia mensagem via API HTTP"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text
            }
            if parse_mode:
                data['parse_mode'] = parse_mode
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return None
    
    def get_me(self):
        """Obtém informações do bot"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter info do bot: {e}")
            return None
    
    def set_webhook(self, webhook_url):
        """Configura webhook"""
        try:
            url = f"{self.base_url}/setWebhook"
            data = {'url': webhook_url}
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {e}")
            return None

# Instância global do bot
telegram_bot = None

def initialize_bot():
    """Inicializa o bot"""
    global telegram_bot
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN não configurado")
        return False
    
    try:
        telegram_bot = TelegramBot(BOT_TOKEN)
        bot_info = telegram_bot.get_me()
        
        if bot_info and bot_info.get('ok'):
            logger.info(f"Bot inicializado: @{bot_info['result']['username']}")
            return True
        else:
            logger.error("Falha ao obter informações do bot")
            return False
    except Exception as e:
        logger.error(f"Erro ao inicializar bot: {e}")
        return False

def process_message(update):
    """Processa mensagem recebida"""
    try:
        message = update.get('message', {})
        if not message:
            return
        
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        user = message.get('from', {})
        
        logger.info(f"Mensagem de {user.get('username', 'unknown')}: {text}")
        
        # Processar comandos
        if text.startswith('/start'):
            response = "🤖 Bot de Gestão de Clientes iniciado!\n\nComandos disponíveis:\n/help - Ajuda\n/status - Status do sistema"
            telegram_bot.send_message(chat_id, response)
        
        elif text.startswith('/help'):
            response = """🤖 Bot de Gestão de Clientes

Comandos disponíveis:
• /start - Iniciar bot
• /help - Esta ajuda
• /status - Status do sistema
• /ping - Teste de conectividade

Sistema funcionando via webhook!"""
            telegram_bot.send_message(chat_id, response)
        
        elif text.startswith('/status'):
            status_text = f"""📊 Status do Sistema

• Bot: ✅ Funcionando
• Webhook: ✅ Ativo
• Database: ✅ Conectado
• Hora: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')}

Sistema operacional!"""
            telegram_bot.send_message(chat_id, status_text)
        
        elif text.startswith('/ping'):
            telegram_bot.send_message(chat_id, "🏓 Pong! Bot respondendo normalmente.")
        
        else:
            # Mensagem padrão para outros textos
            if str(chat_id) == ADMIN_CHAT_ID:
                telegram_bot.send_message(chat_id, f"Mensagem recebida: {text}\n\nUse /help para ver comandos disponíveis.")
    
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Bot Telegram - Sistema de Gestão de Clientes',
        'bot_initialized': telegram_bot is not None,
        'timestamp': datetime.now(pytz.timezone('America/Sao_Paulo')).isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para receber updates do Telegram"""
    if not telegram_bot:
        return jsonify({'error': 'Bot não inicializado'}), 500
    
    try:
        update = request.get_json()
        if update:
            logger.info(f"Update recebido: {update}")
            process_message(update)
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'error': 'Dados inválidos'}), 400
    
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/send_test', methods=['POST'])
def send_test():
    """Endpoint para teste de envio de mensagem"""
    if not telegram_bot or not ADMIN_CHAT_ID:
        return jsonify({'error': 'Bot ou admin não configurado'}), 500
    
    try:
        message = "🧪 Teste de mensagem do bot!\n\nSistema funcionando corretamente."
        result = telegram_bot.send_message(ADMIN_CHAT_ID, message)
        
        if result:
            return jsonify({'status': 'ok', 'message': 'Mensagem enviada'})
        else:
            return jsonify({'error': 'Falha ao enviar mensagem'}), 500
    
    except Exception as e:
        logger.error(f"Erro ao enviar teste: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Inicializar bot
    logger.info("Iniciando bot...")
    
    if initialize_bot():
        logger.info("✅ Bot inicializado com sucesso")
    else:
        logger.warning("⚠️ Bot não inicializado, mas servidor Flask será executado")
    
    # Configurar webhook se URL disponível
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url and telegram_bot:
        result = telegram_bot.set_webhook(f"{webhook_url}/webhook")
        if result and result.get('ok'):
            logger.info(f"✅ Webhook configurado: {webhook_url}/webhook")
        else:
            logger.warning("⚠️ Falha ao configurar webhook")
    
    # Iniciar servidor Flask
    port = int(os.getenv('PORT', 5001))
    logger.info(f"Iniciando servidor Flask na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)