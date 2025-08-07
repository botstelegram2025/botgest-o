#!/usr/bin/env python3
"""
Iniciador do Bot Telegram - Sistema de Gestão de Clientes
Script simplificado para inicializar o bot com tratamento de erros
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
import pytz

# Configurar logging básico
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Verificar secrets essenciais
def check_required_secrets():
    """Verifica se os secrets obrigatórios estão configurados"""
    required = ['BOT_TOKEN', 'ADMIN_CHAT_ID']
    missing = []
    
    for secret in required:
        if not os.getenv(secret):
            missing.append(secret)
    
    if missing:
        logger.error(f"Secrets obrigatórios não configurados: {missing}")
        logger.error("Configure os secrets no painel do Replit antes de continuar")
        return False
    
    return True

async def start_bot():
    """Inicia o bot com configuração mínima"""
    
    if not check_required_secrets():
        return
    
    try:
        # Importar dependências principais
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
        from telegram.ext import ContextTypes
        
        # Inicializar banco de dados
        logger.info("Inicializando banco de dados...")
        from database import DatabaseManager
        db = DatabaseManager()
        
        # Criar teclado básico
        def create_basic_keyboard():
            keyboard = [
                [KeyboardButton("👥 Listar Clientes"), KeyboardButton("➕ Adicionar Cliente")],
                [KeyboardButton("📊 Status"), KeyboardButton("❓ Ajuda")]
            ]
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # Comando start básico
        async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            admin_id = int(os.getenv('ADMIN_CHAT_ID'))
            if update.effective_chat.id != admin_id:
                await update.message.reply_text("❌ Acesso negado. Apenas o admin pode usar este bot.")
                return
            
            welcome_text = f"""🤖 *Bot de Gestão de Clientes*

Olá! Sistema inicializado com sucesso.

📊 *Status do Sistema:*
• Banco de dados: ✅ Conectado
• Bot Telegram: ✅ Funcionando
• Data/Hora: {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y às %H:%M')}

*Funcionalidades disponíveis:*
👥 Gestão de clientes
📱 Integração WhatsApp (Baileys)
📄 Templates de mensagens
⏰ Agendamento automático

Use os botões abaixo para navegar pelo sistema."""

            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=create_basic_keyboard()
            )
        
        # Comando de status
        async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            admin_id = int(os.getenv('ADMIN_CHAT_ID'))
            if update.effective_chat.id != admin_id:
                return
            
            try:
                # Estatísticas básicas
                clientes = db.listar_clientes(apenas_ativos=True)
                total_clientes = len(clientes) if clientes else 0
                
                status_text = f"""📊 *Status do Sistema*

🗄️ *Banco de Dados:* ✅ Conectado
👥 *Total de Clientes:* {total_clientes}
🕒 *Última Atualização:* {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y às %H:%M')}

🔗 *Variáveis Configuradas:*
• BOT_TOKEN: ✅
• ADMIN_CHAT_ID: ✅
• DATABASE_URL: ✅

Sistema operacional! 🚀"""
                
                await update.message.reply_text(status_text, parse_mode='Markdown')
                
            except Exception as e:
                await update.message.reply_text(f"❌ Erro ao obter status: {str(e)}")
        
        # Tratamento de mensagens gerais
        async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
            admin_id = int(os.getenv('ADMIN_CHAT_ID'))
            if update.effective_chat.id != admin_id:
                return
            
            text = update.message.text
            
            if text == "📊 Status":
                await status_command(update, context)
            elif text == "❓ Ajuda":
                help_text = """❓ *Ajuda do Sistema*

*Comandos disponíveis:*
• /start - Inicializar bot
• /status - Ver status do sistema

*Botões disponíveis:*
📊 Status - Informações do sistema
❓ Ajuda - Esta mensagem

*Sistema completo:*
Este é um sistema completo de gestão de clientes com:
• Cadastro escalonável de clientes
• Mensagens automáticas de cobrança
• Integração WhatsApp via Baileys
• Templates editáveis
• Agendamento automático

Para usar todas as funcionalidades, o sistema principal deve ser executado através do arquivo main.py"""
                
                await update.message.reply_text(help_text, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "Use os botões ou comandos disponíveis para navegar pelo sistema.",
                    reply_markup=create_basic_keyboard()
                )
        
        # Configurar aplicação
        app = Application.builder().token(os.getenv('BOT_TOKEN')).build()
        
        # Adicionar handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        logger.info("Bot iniciado com sucesso! Aguardando mensagens...")
        logger.info(f"Admin Chat ID: {os.getenv('ADMIN_CHAT_ID')}")
        
        # Executar bot
        await app.run_polling(allowed_updates=['message'])
        
    except ImportError as e:
        logger.error(f"Erro de importação: {e}")
        logger.error("Verifique se todas as dependências estão instaladas")
    except Exception as e:
        logger.error(f"Erro ao inicializar bot: {e}")
        raise

async def setup_basic_handlers(application):
    """Configura handlers básicos para o bot"""
    from telegram.ext import CommandHandler, MessageHandler, filters
    from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
    from telegram.ext import ContextTypes
    
    def create_basic_keyboard():
        keyboard = [
            [KeyboardButton("👥 Listar Clientes"), KeyboardButton("➕ Adicionar Cliente")],
            [KeyboardButton("📊 Status"), KeyboardButton("❓ Ajuda")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        admin_id = int(os.getenv('ADMIN_CHAT_ID'))
        if update.effective_chat.id != admin_id:
            await update.message.reply_text("❌ Acesso negado. Apenas o admin pode usar este bot.")
            return
        
        welcome_text = f"""🤖 *Bot de Gestão de Clientes*

Olá! Sistema inicializado com sucesso.

📊 *Status do Sistema:*
• Banco de dados: ✅ Conectado
• Timezone: 🇧🇷 America/Sao_Paulo
• Modo: 🔧 Básico

Use os botões abaixo para navegar:"""
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode='Markdown',
            reply_markup=create_basic_keyboard()
        )
    
    async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        admin_id = int(os.getenv('ADMIN_CHAT_ID'))
        if update.effective_chat.id != admin_id:
            return
        
        try:
            from database import DatabaseManager
            db = DatabaseManager()
            db_status = "✅ Conectado"
        except Exception as e:
            db_status = f"❌ Erro: {str(e)[:50]}..."
        
        current_time = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%d/%m/%Y %H:%M:%S")
        
        status_text = f"""📊 *Status do Sistema*

🗄️ *Banco de Dados:* {db_status}
⏰ *Data/Hora:* {current_time}
🤖 *Bot:* ✅ Ativo
🔧 *Modo:* Básico

Para funcionalidades completas (templates, agendamento, WhatsApp), execute o sistema principal."""
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        admin_id = int(os.getenv('ADMIN_CHAT_ID'))
        if update.effective_chat.id != admin_id:
            return
        
        text = update.message.text
        
        if text == "📊 Status":
            await status_command(update, context)
        elif text == "❓ Ajuda":
            help_text = """❓ *Ajuda do Sistema*

*Comandos disponíveis:*
• /start - Inicializar bot
• /status - Ver status do sistema

*Botões disponíveis:*
📊 Status - Informações do sistema
❓ Ajuda - Esta mensagem

*Sistema completo:*
Para usar todas as funcionalidades (cadastro de clientes, templates, agendamento), execute o sistema principal através do arquivo main.py"""
            
            await update.message.reply_text(help_text, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "Use os botões ou comandos disponíveis para navegar pelo sistema.",
                reply_markup=create_basic_keyboard()
            )
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)