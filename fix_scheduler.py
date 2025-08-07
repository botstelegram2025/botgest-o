#!/usr/bin/env python3
"""
Fix do Sistema de Agendamento
Corrige problemas no agendador e força processamento de mensagens pendentes
"""

import os
import sys
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from database import DatabaseManager
from baileys_api import BaileysAPI
from templates import TemplateManager
from utils import agora_br, formatar_data_br

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def processar_vencimentos_hoje():
    """Processa vencimentos de hoje e envia mensagens"""
    try:
        db = DatabaseManager()
        baileys = BaileysAPI()
        template_manager = TemplateManager(db)
        
        logger.info("🔄 Iniciando processamento de vencimentos...")
        
        # Buscar clientes que vencem hoje
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, nome, telefone, pacote, valor, servidor, vencimento
                    FROM clientes 
                    WHERE vencimento = CURRENT_DATE 
                    AND ativo = true
                """)
                clientes_hoje = cursor.fetchall()
        
        if not clientes_hoje:
            logger.info("📭 Nenhum cliente vence hoje")
            return
        
        logger.info(f"📋 {len(clientes_hoje)} cliente(s) vencem hoje")
        
        # Buscar template de vencimento
        template = template_manager.get_template_by_type('vencimento')
        if not template:
            logger.error("❌ Template de vencimento não encontrado")
            return
        
        sucessos = 0
        falhas = 0
        
        for cliente in clientes_hoje:
            try:
                # Preparar dados do cliente
                dados_cliente = {
                    'nome': cliente['nome'],
                    'telefone': cliente['telefone'],
                    'pacote': cliente['pacote'],
                    'valor': f"{cliente['valor']:.2f}",
                    'servidor': cliente['servidor'] or 'Não informado',
                    'vencimento': cliente['vencimento'].strftime('%d/%m/%Y')
                }
                
                # Processar template
                mensagem = template_manager.processar_template(template['conteudo'], dados_cliente)
                
                # Enviar via WhatsApp
                telefone_completo = f"55{cliente['telefone']}"
                resultado = baileys.send_message(telefone_completo, mensagem)
                
                if resultado and resultado.get('success'):
                    logger.info(f"✅ Enviado para {cliente['nome']}: {cliente['telefone']}")
                    sucessos += 1
                    
                    # Registrar log
                    with db.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO logs_envio 
                                (cliente_id, template_id, telefone, mensagem, tipo_envio, sucesso, message_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                cliente['id'], template['id'], cliente['telefone'],
                                mensagem, 'vencimento_hoje', True, 
                                resultado.get('messageId', '')
                            ))
                            conn.commit()
                            
                else:
                    logger.error(f"❌ Falha ao enviar para {cliente['nome']}: {cliente['telefone']}")
                    falhas += 1
                    
                    # Registrar erro
                    with db.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO logs_envio 
                                (cliente_id, template_id, telefone, mensagem, tipo_envio, sucesso, erro)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                cliente['id'], template['id'], cliente['telefone'],
                                mensagem, 'vencimento_hoje', False,
                                str(resultado.get('error', 'Erro desconhecido'))
                            ))
                            conn.commit()
                            
            except Exception as e:
                logger.error(f"❌ Erro ao processar {cliente['nome']}: {e}")
                falhas += 1
        
        logger.info(f"📊 Processamento concluído: {sucessos} sucessos, {falhas} falhas")
        
        # Enviar relatório para admin
        if os.getenv('BOT_TOKEN') and os.getenv('ADMIN_CHAT_ID'):
            relatorio = f"""📋 *RELATÓRIO DE VENCIMENTOS*

📅 *Data:* {datetime.now().strftime('%d/%m/%Y às %H:%M')}
👥 *Clientes processados:* {len(clientes_hoje)}
✅ *Sucessos:* {sucessos}
❌ *Falhas:* {falhas}

🎯 *Sistema funcionando automaticamente!*"""
            
            try:
                requests.post(
                    f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage",
                    data={
                        'chat_id': os.getenv('ADMIN_CHAT_ID'),
                        'text': relatorio,
                        'parse_mode': 'Markdown'
                    },
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Erro ao enviar relatório: {e}")
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")

def processar_fila_mensagens():
    """Processa mensagens da fila"""
    try:
        db = DatabaseManager()
        baileys = BaileysAPI()
        
        logger.info("🔄 Processando fila de mensagens...")
        
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, telefone, mensagem, tipo_mensagem, tentativas, max_tentativas
                    FROM fila_mensagens 
                    WHERE processado = false 
                    AND agendado_para <= NOW()
                    AND tentativas < max_tentativas
                    LIMIT 10
                """)
                mensagens = cursor.fetchall()
        
        if not mensagens:
            logger.info("📭 Nenhuma mensagem na fila")
            return
        
        logger.info(f"📋 Processando {len(mensagens)} mensagem(s)")
        
        for msg in mensagens:
            try:
                # Tentar enviar
                resultado = baileys.send_message(f"55{msg['telefone']}", msg['mensagem'])
                
                with db.get_connection() as conn:
                    with conn.cursor() as cursor:
                        if resultado and resultado.get('success'):
                            # Marcar como processada
                            cursor.execute("""
                                UPDATE fila_mensagens 
                                SET processado = true, data_processamento = NOW()
                                WHERE id = %s
                            """, (msg['id'],))
                            logger.info(f"✅ Mensagem {msg['id']} enviada")
                        else:
                            # Incrementar tentativas
                            cursor.execute("""
                                UPDATE fila_mensagens 
                                SET tentativas = tentativas + 1
                                WHERE id = %s
                            """, (msg['id'],))
                            logger.error(f"❌ Falha na mensagem {msg['id']}")
                        
                        conn.commit()
                        
            except Exception as e:
                logger.error(f"Erro ao processar mensagem {msg['id']}: {e}")
        
    except Exception as e:
        logger.error(f"Erro ao processar fila: {e}")

if __name__ == "__main__":
    logger.info("🚀 Iniciando fix do agendador...")
    
    # Processar vencimentos de hoje
    processar_vencimentos_hoje()
    
    # Processar fila de mensagens
    processar_fila_mensagens()
    
    logger.info("✅ Fix do agendador concluído!")