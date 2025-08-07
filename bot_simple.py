#!/usr/bin/env python3
"""
Bot Telegram simples e funcional
"""
import os
import logging
from flask import Flask, request, jsonify
import asyncio

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variáveis globais
bot_app = None

def test_telegram_imports():
    """Testa importações do telegram"""
    try:
        import telegram
        logger.info("telegram importado com sucesso")
        
        from telegram.ext import Application
        logger.info("Application importado com sucesso")
        
        return True
    except ImportError as e:
        logger.error(f"Erro ao importar telegram: {e}")
        return False

async def create_simple_bot():
    """Cria um bot telegram simples"""
    global bot_app
    
    try:
        # Verificar token
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("BOT_TOKEN não configurado")
            return False
        
        # Testar importações primeiro
        if not test_telegram_imports():
            logger.error("Falha nos imports do telegram")
            return False
        
        # Importar após teste
        from telegram.ext import Application, CommandHandler
        
        # Criar aplicação
        bot_app = Application.builder().token(token).build()
        
        # Handler simples
        async def start_command(update, context):
            """Comando /start"""
            await update.message.reply_text("Bot funcionando! 🤖")
        
        # Adicionar handler
        bot_app.add_handler(CommandHandler("start", start_command))
        
        logger.info("Bot criado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar bot: {e}")
        return False

@app.route('/')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'Bot Telegram',
        'bot_configured': bot_app is not None
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook do telegram"""
    if not bot_app:
        return jsonify({'error': 'Bot não inicializado'}), 500
    
    try:
        # Processar update
        json_data = request.get_json()
        logger.info(f"Update recebido: {json_data}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Inicializar bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bot_created = loop.run_until_complete(create_simple_bot())
    
    if bot_created:
        logger.info("Bot inicializado com sucesso")
    else:
        logger.warning("Bot não foi inicializado, mas servidor Flask vai rodar")
    
    # Iniciar Flask
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)