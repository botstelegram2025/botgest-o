#!/usr/bin/env python3
"""
Script para corrigir e inicializar o bot Telegram
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Testa todas as importações necessárias"""
    try:
        # Testar importação básica
        import telegram
        logger.info("✅ telegram importado")
        
        # Testar Application
        from telegram.ext import Application
        logger.info("✅ Application importado")
        
        # Testar handlers
        from telegram.ext import CommandHandler, MessageHandler, filters
        logger.info("✅ Handlers importados")
        
        # Testar Update
        from telegram import Update
        logger.info("✅ Update importado")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Erro de importação: {e}")
        return False

def create_basic_bot():
    """Cria um bot básico funcional"""
    if not test_imports():
        return False
    
    try:
        from telegram.ext import Application, CommandHandler
        
        # Verificar token
        token = os.getenv('BOT_TOKEN')
        if not token:
            logger.error("❌ BOT_TOKEN não encontrado")
            return False
        
        # Criar bot
        app = Application.builder().token(token).build()
        
        # Handler de teste
        async def start(update, context):
            await update.message.reply_text("Bot funcionando! 🤖")
        
        app.add_handler(CommandHandler("start", start))
        
        logger.info("✅ Bot criado com sucesso")
        return app
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar bot: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testando configuração do bot...")
    
    if test_imports():
        print("✅ Todas as importações funcionando")
        bot = create_basic_bot()
        if bot:
            print("✅ Bot configurado com sucesso!")
        else:
            print("❌ Falha ao configurar bot")
    else:
        print("❌ Problemas com importações")