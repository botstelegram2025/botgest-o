#!/usr/bin/env python3
"""
Teste da instalação do python-telegram-bot
"""

import os
import sys

def test_telegram_imports():
    """Testa imports do telegram bot"""
    try:
        print("Testando import básico...")
        import telegram
        print(f"✅ telegram importado: {telegram}")
        
        print("Testando diretório telegram...")
        print(f"Telegram dir: {dir(telegram)}")
        
        print("Testando import de Chat...")
        from telegram import Chat
        print(f"✅ Chat importado: {Chat}")
        
        print("Testando import de Application...")
        from telegram.ext import Application
        print(f"✅ Application importado: {Application}")
        
        print("✅ Todos os imports funcionaram!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_basic_bot():
    """Testa criação básica de bot"""
    try:
        from telegram.ext import Application
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            print("❌ BOT_TOKEN não configurado")
            return False
        
        app = Application.builder().token(bot_token).build()
        print(f"✅ Bot application criado: {type(app)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar bot: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Testando instalação do python-telegram-bot...")
    
    if test_telegram_imports():
        print("\n🔍 Testando criação de bot...")
        test_basic_bot()
    
    print("\n✅ Teste concluído")