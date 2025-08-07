# 📦 Arquivos Necessários para Deploy Railway

## ✅ Arquivos OBRIGATÓRIOS (Raiz do Projeto):

### **Código Principal:**
- `bot_complete.py` - Bot Telegram principal
- `baileys_api.py` - Interface com API WhatsApp
- `database.py` - Configurações do banco PostgreSQL
- `templates.py` - Sistema de templates de mensagens
- `config.py` - Configurações gerais
- `utils.py` - Funções utilitárias
- `models.py` - Modelos de dados

### **Configurações de Deploy:**
- `railway.json` - Configuração específica Railway
- `Dockerfile.railway` - Container otimizado
- `setup_railway.sh` - Script de inicialização
- `start.sh` - Script de start
- `pyproject.toml` - Dependências Python
- `requirements.txt` - (será gerado automaticamente)

### **Documentação:**
- `README.md` - Descrição do projeto
- `RAILWAY_DEPLOY.md` - Guia de deploy
- `.gitignore` - Arquivos a ignorar

## 📁 Pasta `baileys-server/` (COMPLETA):

### **Arquivos Node.js:**
- `package.json` - Dependências Node.js
- `server.js` - Servidor API WhatsApp
- `start.sh` - Script de inicialização

### **Autenticação WhatsApp (auth_info/):**
- `creds.json` - Credenciais de autenticação
- Todos os arquivos `pre-key-*.json`
- Todos os arquivos `sender-key-*.json`
- Arquivos de sessão existentes

## 🚫 Arquivos a EXCLUIR:

### **Não incluir:**
- `.replit` - Específico do Replit
- `replit.md` - Documentação interna
- `app.py` - Versão Flask (não usada)
- `bot_simple.py` - Versão simplificada
- `bot_working.py` - Versão de desenvolvimento
- `fix_bot.py` - Script de correção
- `test_*.py` - Arquivos de teste
- `process_pending.py` - Script avulso
- `.cache/` - Cache temporário
- `__pycache__/` - Cache Python
- `node_modules/` - Dependências Node (serão instaladas)

## 🔧 Como Preparar:

### **Opção 1 - Download Replit:**
1. Menu (...) → "Download as ZIP"
2. Extrair e remover arquivos desnecessários
3. Manter apenas arquivos da lista acima

### **Opção 2 - Seleção Manual:**
1. Criar pasta local `bot-gestao-clientes/`
2. Copiar arquivos obrigatórios
3. Criar estrutura `baileys-server/` com subpasta `auth_info/`

## 📋 Estrutura Final:
```
bot-gestao-clientes/
├── bot_complete.py
├── baileys_api.py
├── database.py
├── templates.py
├── config.py
├── utils.py
├── models.py
├── railway.json
├── Dockerfile.railway
├── setup_railway.sh
├── start.sh
├── pyproject.toml
├── README.md
├── RAILWAY_DEPLOY.md
├── .gitignore
└── baileys-server/
    ├── package.json
    ├── server.js
    ├── start.sh
    └── auth_info/
        ├── creds.json
        ├── pre-key-*.json
        └── sender-key-*.json
```

## ⚡ Variáveis de Ambiente Railway:
```
BOT_TOKEN=seu_token_telegram
ADMIN_CHAT_ID=seu_chat_id
DATABASE_URL=postgresql://... (automático)
PORT=5000 (automático)
```

## 🚀 Processo no Railway:
1. Upload/push dos arquivos
2. Railway detecta Dockerfile.railway
3. Build automático
4. Deploy com PostgreSQL incluído
5. Bot roda 24/7

**Total de arquivos:** ~20 principais + pasta auth_info completa