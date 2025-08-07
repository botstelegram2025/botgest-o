#!/usr/bin/env python3
"""
Teste básico do sistema - Verificar componentes principais
"""

import os
import sys
import logging
from datetime import datetime
import pytz

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    """Testa conexão com banco de dados"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        logger.info("✅ Banco de dados conectado com sucesso")
        
        # Testar listagem de clientes
        clientes = db.listar_clientes()
        logger.info(f"📊 Total de clientes no banco: {len(clientes) if clientes else 0}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro no banco de dados: {e}")
        return False

def test_secrets():
    """Testa se os secrets estão configurados"""
    required = ['BOT_TOKEN', 'ADMIN_CHAT_ID', 'DATABASE_URL']
    missing = []
    
    for secret in required:
        if not os.getenv(secret):
            missing.append(secret)
    
    if missing:
        logger.error(f"❌ Secrets não configurados: {missing}")
        return False
    else:
        logger.info("✅ Todos os secrets estão configurados")
        return True

def test_imports():
    """Testa imports essenciais"""
    try:
        import psycopg2
        logger.info("✅ psycopg2 importado")
        
        import pytz
        logger.info("✅ pytz importado")
        
        # Testar timezone brasileiro
        tz = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(tz)
        logger.info(f"✅ Timezone Brasil: {agora.strftime('%d/%m/%Y %H:%M:%S')}")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Erro de import: {e}")
        return False

def main():
    """Função principal de teste"""
    logger.info("🔍 Iniciando testes do sistema...")
    
    results = {
        'secrets': test_secrets(),
        'imports': test_imports(),
        'database': test_database()
    }
    
    logger.info("\n📋 Resultados dos testes:")
    for test, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"  {test.upper()}: {status}")
    
    if all(results.values()):
        logger.info("\n🎉 Todos os testes passaram! Sistema básico funcionando.")
        logger.info("📱 Próximo passo: Configurar bot Telegram")
    else:
        logger.error("\n⚠️ Alguns testes falharam. Verifique as configurações.")
        return False
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"💥 Erro fatal: {e}")
        sys.exit(1)