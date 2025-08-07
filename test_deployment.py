#!/usr/bin/env python3
"""
Script de teste para validar deployment readiness
"""

import requests
import json
import sys
import time

def test_health_endpoint():
    """Testa o endpoint de health check"""
    try:
        response = requests.get('http://localhost:5000/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check Endpoint: OK")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_status_endpoint():
    """Testa o endpoint de status detalhado"""
    try:
        response = requests.get('http://localhost:5000/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Status Endpoint: OK")
            print(f"   Bot Initialized: {data.get('bot_initialized')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Secrets: {data.get('secrets_configured')}")
            return True
        else:
            print(f"❌ Status Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status Error: {e}")
        return False

def main():
    print("🚀 Testando deployment readiness...\n")
    
    # Aguardar servidor estar ready
    print("⏳ Aguardando servidor...")
    time.sleep(2)
    
    health_ok = test_health_endpoint()
    status_ok = test_status_endpoint()
    
    print(f"\n📊 Resultados:")
    if health_ok and status_ok:
        print("🎉 Deployment Ready! Todos os endpoints funcionando.")
        print("\n📋 Próximos passos para deploy:")
        print("   1. Configurar secrets: BOT_TOKEN, ADMIN_CHAT_ID")
        print("   2. Deploy via Replit Deployments")
        print("   3. Configurar webhook do Telegram (se necessário)")
        return 0
    else:
        print("⚠️  Alguns problemas encontrados. Verifique os logs.")
        return 1

if __name__ == '__main__':
    sys.exit(main())