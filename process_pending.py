#!/usr/bin/env python3
"""
Script para processar mensagens pendentes do Telegram
"""
import os
import requests
import json
from bot_complete import telegram_bot

def process_pending_messages():
    """Processa todas as mensagens pendentes"""
    if not telegram_bot:
        print("Bot não inicializado")
        return
    
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        print("BOT_TOKEN não configurado")
        return
    
    try:
        # Buscar updates pendentes
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                updates = data.get('result', [])
                print(f"Processando {len(updates)} mensagens pendentes...")
                
                for update in updates:
                    print(f"Processando update: {update.get('update_id')}")
                    telegram_bot.process_message(update)
                
                # Marcar como processadas
                if updates:
                    last_update_id = updates[-1]['update_id']
                    offset_response = requests.get(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                        params={'offset': last_update_id + 1},
                        timeout=10
                    )
                    print(f"Mensagens marcadas como processadas até ID: {last_update_id}")
                
                print("✅ Mensagens pendentes processadas!")
            else:
                print(f"Erro na API: {data}")
        else:
            print(f"Erro HTTP: {response.status_code}")
    
    except Exception as e:
        print(f"Erro ao processar mensagens: {e}")

if __name__ == '__main__':
    process_pending_messages()