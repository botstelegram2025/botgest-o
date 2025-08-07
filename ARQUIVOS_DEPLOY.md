# 📦 Lista Completa de Arquivos para Deploy Railway

## 🎯 **Método Recomendado: Download ZIP do Replit**

1. **No Replit:** Menu (...) → "Download as ZIP"
2. **Extrair arquivo** baixado
3. **Upload para GitHub** ou Railway

## 📁 **Arquivos Essenciais Incluídos:**

### **🤖 Bot & Sistema Principal**
```
bot_complete.py          # Bot Telegram principal
database.py              # Conexão PostgreSQL
templates.py             # Sistema de templates
config.py               # Configurações
scheduler.py            # Agendador de tarefas
```

### **📱 WhatsApp/Baileys**
```
baileys-server/
├── server.js           # API Node.js
├── package.json        # Dependências Node
├── auth_info/          # Sessões WhatsApp (IMPORTANTE!)
│   ├── creds.json
│   └── session-*.json
```

### **🚀 Deploy Railway**
```
railway.json            # Configuração Railway
Dockerfile.railway      # Container otimizado
start_railway.py        # Script de inicialização
setup_railway.sh        # Setup automático
```

### **📋 Configurações Python**
```
pyproject.toml          # Dependências Python
uv.lock                 # Lock de versões
requirements.txt        # Pip fallback (se necessário)
```

### **📖 Documentação**
```
RAILWAY_DEPLOY.md       # Guia completo de deploy
WHATSAPP_SETUP.md       # Setup WhatsApp
BAILEYS_API_SETUP.md    # Setup API
COMO_FAZER_COMMIT.md    # Como fazer commit
```

### **⚙️ Arquivos de Sistema**
```
.gitignore             # Exclusões git
.env.example           # Exemplo de variáveis
Procfile              # Para Heroku (opcional)
runtime.txt           # Versão Python
```

## 🎯 **Arquivos de Sessão WhatsApp (CRÍTICOS!)**

**MUITO IMPORTANTE:** Os arquivos em `baileys-server/auth_info/` contêm sua sessão WhatsApp atual:
- `creds.json` - Credenciais de autenticação
- `session-*.json` - Dados da sessão ativa
- `pre-key-*.json` - Chaves de segurança

**Se incluir estes arquivos** → WhatsApp já conectado no Railway
**Se excluir estes arquivos** → Precisará escanear QR Code novamente

## ✅ **O que NÃO incluir (já no .gitignore):**
- `__pycache__/`
- `node_modules/`
- `.env` (variáveis locais)
- `.cache/`

## 🚀 **Após Download:**

1. **Extrair ZIP**
2. **Verificar se tem** `baileys-server/auth_info/`
3. **Criar repo GitHub**
4. **Upload todos os arquivos**
5. **Railway conecta automaticamente**

## 💡 **Dica Extra:**
O arquivo ZIP do Replit já vem com **TUDO** configurado e pronto para funcionar no Railway imediatamente!