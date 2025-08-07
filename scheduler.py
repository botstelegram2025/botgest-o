"""
Sistema de Agendamento de Mensagens
Gerencia envios automáticos baseados em vencimentos e agenda mensagens personalizadas
"""

import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from utils import agora_br, formatar_data_br, formatar_datetime_br
import pytz

logger = logging.getLogger(__name__)

class MessageScheduler:
    def __init__(self, database_manager, baileys_api, template_manager):
        """Inicializa o agendador de mensagens"""
        self.db = database_manager
        self.baileys_api = baileys_api
        self.template_manager = template_manager
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('America/Sao_Paulo'))
        self.running = False
        self.ultima_verificacao_time = None
        
        # Configurar jobs principais
        self._setup_main_jobs()
    
    def _setup_main_jobs(self):
        """Configura os jobs principais do sistema"""
        
        # Verificação de mensagens pendentes a cada 5 minutos
        self.scheduler.add_job(
            func=self._processar_fila_mensagens,
            trigger=CronTrigger(minute='*/5'),
            id='processar_fila',
            name='Processar Fila de Mensagens',
            replace_existing=True
        )
        
        # Agendamento diário de novas mensagens às 8:00
        self.scheduler.add_job(
            func=self._agendar_mensagens_diarias,
            trigger=CronTrigger(hour=8, minute=0),
            id='agendar_diario',
            name='Agendar Mensagens Diárias',
            replace_existing=True
        )
        
        # Limpeza da fila às 2:00 da madrugada
        self.scheduler.add_job(
            func=self._limpar_fila_antiga,
            trigger=CronTrigger(hour=2, minute=0),
            id='limpar_fila',
            name='Limpar Fila Antiga',
            replace_existing=True
        )
        
        logger.info("Jobs principais do agendador configurados")
    
    def start(self):
        """Inicia o agendador"""
        try:
            if not self.running:
                self.scheduler.start()
                self.running = True
                logger.info("Agendador de mensagens iniciado com sucesso!")
                
                # Executar agendamento inicial
                asyncio.create_task(self._agendar_mensagens_diarias())
        except Exception as e:
            logger.error(f"Erro ao iniciar agendador: {e}")
    
    def stop(self):
        """Para o agendador"""
        try:
            if self.running:
                self.scheduler.shutdown()
                self.running = False
                logger.info("Agendador de mensagens parado")
        except Exception as e:
            logger.error(f"Erro ao parar agendador: {e}")
    
    def is_running(self):
        """Verifica se o agendador está rodando"""
        return self.running and self.scheduler.running
    
    def ultima_verificacao(self):
        """Retorna a última verificação formatada"""
        if self.ultima_verificacao_time:
            return formatar_datetime_br(self.ultima_verificacao_time)
        return "Nunca executado"
    
    async def _processar_fila_mensagens(self):
        """Processa mensagens pendentes na fila"""
        try:
            self.ultima_verificacao_time = agora_br()
            logger.info("Iniciando processamento da fila de mensagens...")
            
            # Buscar mensagens pendentes
            mensagens_pendentes = self.db.obter_mensagens_pendentes(limit=50)
            
            if not mensagens_pendentes:
                logger.info("Nenhuma mensagem pendente para processamento")
                return
            
            logger.info(f"Processando {len(mensagens_pendentes)} mensagens pendentes")
            
            for mensagem in mensagens_pendentes:
                try:
                    await self._enviar_mensagem_fila(mensagem)
                    # Aguardar entre envios para não sobrecarregar
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Erro ao processar mensagem ID {mensagem['id']}: {e}")
                    self.db.marcar_mensagem_processada(mensagem['id'], False, str(e))
            
            logger.info("Processamento da fila concluído")
            
        except Exception as e:
            logger.error(f"Erro no processamento da fila: {e}")
    
    async def _enviar_mensagem_fila(self, mensagem):
        """Envia uma mensagem da fila"""
        try:
            # Verificar se cliente ainda está ativo
            cliente = self.db.buscar_cliente_por_id(mensagem['cliente_id'])
            if not cliente or not cliente['ativo']:
                logger.info(f"Cliente {mensagem['cliente_id']} inativo, removendo da fila")
                self.db.marcar_mensagem_processada(mensagem['id'], True)
                return
            
            # Enviar mensagem via Baileys
            resultado = self.baileys_api.send_message(
                phone=mensagem['telefone'],
                message=mensagem['mensagem']
            )
            
            if resultado['success']:
                # Registrar envio bem-sucedido
                self.db.registrar_envio(
                    cliente_id=mensagem['cliente_id'],
                    template_id=mensagem['template_id'],
                    telefone=mensagem['telefone'],
                    mensagem=mensagem['mensagem'],
                    tipo_envio='automatico',
                    sucesso=True,
                    message_id=resultado.get('message_id')
                )
                
                # Marcar como processado
                self.db.marcar_mensagem_processada(mensagem['id'], True)
                
                logger.info(f"Mensagem enviada com sucesso para {mensagem['cliente_nome']} ({mensagem['telefone']})")
                
            else:
                # Registrar falha
                erro = resultado.get('error', 'Erro desconhecido')
                
                self.db.registrar_envio(
                    cliente_id=mensagem['cliente_id'],
                    template_id=mensagem['template_id'],
                    telefone=mensagem['telefone'],
                    mensagem=mensagem['mensagem'],
                    tipo_envio='automatico',
                    sucesso=False,
                    erro=erro
                )
                
                # Incrementar tentativas
                self.db.marcar_mensagem_processada(mensagem['id'], False, erro)
                
                logger.error(f"Falha ao enviar mensagem para {mensagem['cliente_nome']}: {erro}")
        
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem da fila: {e}")
            self.db.marcar_mensagem_processada(mensagem['id'], False, str(e))
    
    async def _agendar_mensagens_diarias(self):
        """Agenda mensagens para os próximos dias baseado em vencimentos"""
        try:
            logger.info("Iniciando agendamento de mensagens diárias...")
            
            # Buscar clientes ativos
            clientes = self.db.listar_clientes(apenas_ativos=True)
            
            if not clientes:
                logger.info("Nenhum cliente ativo encontrado")
                return
            
            contador_agendadas = 0
            hoje = agora_br().date()
            
            for cliente in clientes:
                try:
                    vencimento = cliente['vencimento']
                    
                    # Calcular datas para agendamento
                    data_2dias_antes = vencimento - timedelta(days=2)
                    data_vencimento = vencimento
                    data_1dia_apos = vencimento + timedelta(days=1)
                    
                    # Agendar mensagem 2 dias antes (se ainda não passou)
                    if data_2dias_antes >= hoje:
                        await self._agendar_mensagem_vencimento(
                            cliente, 'vencimento_2dias', data_2dias_antes
                        )
                        contador_agendadas += 1
                    
                    # Agendar mensagem no dia do vencimento
                    if data_vencimento >= hoje:
                        await self._agendar_mensagem_vencimento(
                            cliente, 'vencimento_hoje', data_vencimento
                        )
                        contador_agendadas += 1
                    
                    # Agendar mensagem 1 dia após (se vencimento já passou)
                    if data_1dia_apos >= hoje and vencimento < hoje:
                        await self._agendar_mensagem_vencimento(
                            cliente, 'vencimento_1dia_apos', data_1dia_apos
                        )
                        contador_agendadas += 1
                        
                except Exception as e:
                    logger.error(f"Erro ao agendar mensagens para cliente {cliente['nome']}: {e}")
            
            logger.info(f"Agendamento concluído: {contador_agendadas} mensagens agendadas")
            
        except Exception as e:
            logger.error(f"Erro no agendamento diário: {e}")
    
    async def _agendar_mensagem_vencimento(self, cliente, tipo_template, data_envio):
        """Agenda mensagem específica de vencimento"""
        try:
            # Buscar template correspondente
            template = self.db.obter_template_por_tipo(tipo_template)
            if not template:
                logger.warning(f"Template {tipo_template} não encontrado")
                return
            
            # Processar template com dados do cliente
            mensagem = self.template_manager.processar_template(template['conteudo'], cliente)
            
            # Calcular horário de envio (9:00 da manhã)
            datetime_envio = datetime.combine(data_envio, datetime.min.time().replace(hour=9))
            datetime_envio = pytz.timezone('America/Sao_Paulo').localize(datetime_envio)
            
            # Verificar se já existe mensagem agendada similar
            mensagens_existentes = self.db.obter_mensagens_pendentes()
            for msg in mensagens_existentes:
                if (msg['cliente_id'] == cliente['id'] and 
                    msg['tipo_mensagem'] == tipo_template and
                    msg['agendado_para'].date() == data_envio):
                    logger.info(f"Mensagem {tipo_template} já agendada para {cliente['nome']}")
                    return
            
            # Adicionar na fila
            self.db.adicionar_fila_mensagem(
                cliente_id=cliente['id'],
                template_id=template['id'],
                telefone=cliente['telefone'],
                mensagem=mensagem,
                tipo_mensagem=tipo_template,
                agendado_para=datetime_envio
            )
            
            logger.info(f"Mensagem {tipo_template} agendada para {cliente['nome']} em {formatar_data_br(data_envio)}")
            
        except Exception as e:
            logger.error(f"Erro ao agendar mensagem de vencimento: {e}")
    
    async def _limpar_fila_antiga(self):
        """Remove mensagens antigas processadas da fila"""
        try:
            logger.info("Iniciando limpeza da fila antiga...")
            
            removidas = self.db.limpar_fila_processadas(dias=7)
            
            logger.info(f"Limpeza concluída: {removidas} mensagens antigas removidas")
            
        except Exception as e:
            logger.error(f"Erro na limpeza da fila: {e}")
    
    def agendar_mensagens_cliente(self, cliente_id):
        """Agenda mensagens para um cliente específico (usado no cadastro)"""
        try:
            cliente = self.db.buscar_cliente_por_id(cliente_id)
            if not cliente:
                return
            
            # Executar agendamento em background
            asyncio.create_task(self._agendar_mensagens_cliente_async(cliente))
            
        except Exception as e:
            logger.error(f"Erro ao agendar mensagens para cliente {cliente_id}: {e}")
    
    async def _agendar_mensagens_cliente_async(self, cliente):
        """Agenda mensagens para cliente específico (versão async)"""
        try:
            hoje = agora_br().date()
            vencimento = cliente['vencimento']
            
            # Agendar boas vindas (imediato)
            template_boas_vindas = self.db.obter_template_por_tipo('boas_vindas')
            if template_boas_vindas:
                mensagem_boas_vindas = self.template_manager.processar_template(
                    template_boas_vindas['conteudo'], cliente
                )
                
                # Agendar para 5 minutos a partir de agora
                agendado_para = agora_br() + timedelta(minutes=5)
                
                self.db.adicionar_fila_mensagem(
                    cliente_id=cliente['id'],
                    template_id=template_boas_vindas['id'],
                    telefone=cliente['telefone'],
                    mensagem=mensagem_boas_vindas,
                    tipo_mensagem='boas_vindas',
                    agendado_para=agendado_para
                )
            
            # Agendar mensagens de vencimento
            data_2dias_antes = vencimento - timedelta(days=2)
            data_vencimento = vencimento
            data_1dia_apos = vencimento + timedelta(days=1)
            
            if data_2dias_antes >= hoje:
                await self._agendar_mensagem_vencimento(
                    cliente, 'vencimento_2dias', data_2dias_antes
                )
            
            if data_vencimento >= hoje:
                await self._agendar_mensagem_vencimento(
                    cliente, 'vencimento_hoje', data_vencimento
                )
            
            if data_1dia_apos >= hoje:
                await self._agendar_mensagem_vencimento(
                    cliente, 'vencimento_1dia_apos', data_1dia_apos
                )
            
            logger.info(f"Mensagens agendadas para novo cliente: {cliente['nome']}")
            
        except Exception as e:
            logger.error(f"Erro ao agendar mensagens para cliente: {e}")
    
    def agendar_mensagem_personalizada(self, cliente_id, template_id, data_hora):
        """Agenda mensagem personalizada"""
        try:
            cliente = self.db.buscar_cliente_por_id(cliente_id)
            template = self.db.obter_template(template_id)
            
            if not cliente or not template:
                return False
            
            # Processar template
            mensagem = self.template_manager.processar_template(template['conteudo'], cliente)
            
            # Adicionar na fila
            fila_id = self.db.adicionar_fila_mensagem(
                cliente_id=cliente_id,
                template_id=template_id,
                telefone=cliente['telefone'],
                mensagem=mensagem,
                tipo_mensagem='personalizada',
                agendado_para=data_hora
            )
            
            logger.info(f"Mensagem personalizada agendada para {cliente['nome']} - ID: {fila_id}")
            return fila_id
            
        except Exception as e:
            logger.error(f"Erro ao agendar mensagem personalizada: {e}")
            return False
    
    def reagendar_todas_mensagens(self):
        """Reagenda todas as mensagens baseado nos vencimentos atuais"""
        try:
            # Limpar fila atual de mensagens não processadas
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM fila_mensagens WHERE processado = FALSE")
                    conn.commit()
            
            # Executar novo agendamento
            asyncio.create_task(self._agendar_mensagens_diarias())
            
            logger.info("Reagendamento de todas as mensagens iniciado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reagendar mensagens: {e}")
            return False
    
    def obter_tarefas_pendentes(self):
        """Obtém lista de tarefas pendentes"""
        try:
            mensagens = self.db.obter_mensagens_pendentes(limit=100)
            
            tarefas = []
            for msg in mensagens:
                tarefas.append({
                    'id': msg['id'],
                    'cliente': msg['cliente_nome'],
                    'telefone': msg['telefone'],
                    'tipo': msg['tipo_mensagem'],
                    'agendado_para': msg['agendado_para'],
                    'tentativas': msg['tentativas']
                })
            
            return tarefas
            
        except Exception as e:
            logger.error(f"Erro ao obter tarefas pendentes: {e}")
            return []
    
    def obter_proximas_execucoes(self, limit=10):
        """Obtém próximas execuções agendadas"""
        try:
            mensagens = self.db.obter_mensagens_pendentes(limit=limit)
            
            execucoes = []
            for msg in mensagens:
                execucoes.append({
                    'data': formatar_datetime_br(msg['agendado_para']),
                    'tipo': msg['tipo_mensagem'],
                    'cliente': msg['cliente_nome'],
                    'telefone': msg['telefone']
                })
            
            return execucoes
            
        except Exception as e:
            logger.error(f"Erro ao obter próximas execuções: {e}")
            return []
    
    def obter_fila_mensagens(self):
        """Obtém fila completa de mensagens"""
        return self.obter_tarefas_pendentes()
