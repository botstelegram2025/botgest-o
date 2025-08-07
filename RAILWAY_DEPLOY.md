# 🚀 Deploy do Bot no Railway

## 💰 Custos Railway:
- **Plano Gratuito**: $5 de crédito mensal
- **Hobby Plan**: $5/mês (uso ilimitado)
- **Custo estimado**: ~$2-3/mês para bot pequeno

## 📋 Pré-requisitos:
1. Conta no Railway (railway.app)
2. Conta no GitHub
3. Variáveis de ambiente configuradas

## 🔧 Passo a Passo:

### 1. Preparar Repositório
```bash
# Inicializar git (se não existir)
git init

# Adicionar arquivos
git add .

# Commit inicial
git commit -m "Bot de Gestão de Clientes - Deploy Railway"

# Conectar com GitHub (criar repo primeiro)
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

### 2. Deploy no Railway
1. Acesse railway.app
2. Clique em "New Project"
3. Conecte com GitHub
4. Selecione seu repositório
5. Railway detectará automaticamente como projeto Python

### 3. Configurar Variáveis de Ambiente
No painel do Railway, adicione:
```
BOT_TOKEN=seu_token_do_telegram
ADMIN_CHAT_ID=seu_chat_id
DATABASE_URL=postgresql://... (Railway fornecerá)
```

### 4. Configurar Database
1. No Railway, adicione PostgreSQL
2. Copie a DATABASE_URL gerada
3. Cole nas variáveis de ambiente

### 5. Deploy Automático
- Railway fará deploy automaticamente
- Bot ficará ativo 24/7
- Logs disponíveis no painel

## ⚙️ Arquivos de Configuração:
- `railway.json` - Configurações do Railway
- `Dockerfile.railway` - Container customizado (sem dependências Replit)
- `start_railway.py` - Script de inicialização para Railway
- `package.json` - Dependências Node.js (Baileys)

## 🔧 Correções Aplicadas:
- ✅ Removidas dependências específicas do Replit
- ✅ Dockerfile otimizado para Railway
- ✅ Script de inicialização dedicado
- ✅ Instalação direta de dependências Python

## 🔄 Comandos Úteis:
```bash
# Ver logs
railway logs

# Redeploy
railway up

# Conectar ao banco
railway connect database
```

## 📊 Monitoramento:
- Logs em tempo real no painel
- Métricas de CPU/RAM
- Alertas de erro automáticos

## 💡 Vantagens Railway vs Replit:
- ✅ Mais barato ($2-3/mês vs $20/mês)
- ✅ Deploy automático via Git
- ✅ Database PostgreSQL incluído
- ✅ Melhor para produção
- ✅ Logs e monitoramento