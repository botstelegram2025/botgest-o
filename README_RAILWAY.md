# 🚀 Bot de Gestão de Clientes - Deploy Railway

## 📦 Conteúdo do Pacote
Este ZIP contém tudo que você precisa para fazer deploy no Railway:

### 📁 Estrutura de Arquivos:
```
├── baileys-server/          # API WhatsApp (Node.js)
│   ├── server.js           # Servidor Baileys
│   └── package.json        # Dependências Node.js
├── *.py                    # Código Python do bot
├── Dockerfile.railway      # Container otimizado
├── start_railway.py        # Script de inicialização
├── railway.json           # Configurações Railway
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de variáveis
└── documentação...

```

## 🎯 Deploy em 5 Passos:

### 1. **Preparar Repositório GitHub**
```bash
# Extrair ZIP e navegar para pasta
cd railway-deploy

# Inicializar git
git init
git add .
git commit -m "Bot Gestão Clientes - Railway Deploy"

# Conectar com GitHub (criar repo primeiro)
git remote add origin https://github.com/SEU_USUARIO/bot-gestao-clientes.git
git push -u origin main
```

### 2. **Deploy no Railway**
1. Acesse [railway.app](https://railway.app)
2. Clique "New Project"
3. Conecte com GitHub
4. Selecione seu repositório
5. Railway detectará automaticamente

### 3. **Adicionar PostgreSQL**
1. No projeto Railway, clique "Add Service"
2. Selecione "PostgreSQL"
3. Railway criará DATABASE_URL automaticamente

### 4. **Configurar Variáveis**
No painel Railway, adicione:
```
BOT_TOKEN=seu_token_telegram
ADMIN_CHAT_ID=seu_chat_id
```

### 5. **Conectar WhatsApp**
1. Aguarde deploy completar
2. Acesse: `https://seu-app.railway.app:3000/qr`
3. Escaneie QR Code com WhatsApp
4. ✅ Pronto! Bot funcionando 24/7

## 💰 Custos:
- **Hobby Plan**: $5/mês
- **Uso real**: ~$2-3/mês

## 🔧 Funcionalidades:
- ✅ Gestão completa de clientes
- ✅ Templates de mensagens
- ✅ WhatsApp integrado (Baileys)
- ✅ Relatórios avançados
- ✅ Agendamento automático
- ✅ Interface Telegram
- ✅ Deploy automático

## 📞 Suporte:
Qualquer dúvida, o bot inclui documentação completa nos arquivos `.md`

**🎉 Seu bot estará rodando 24/7 no Railway!**