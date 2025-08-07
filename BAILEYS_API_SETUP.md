# Como Configurar API Baileys para WhatsApp

## O que é a API Baileys?

A API Baileys é um servidor Node.js que conecta com WhatsApp Web para enviar mensagens automaticamente. É necessária para que o bot possa enviar mensagens WhatsApp.

## Opção 1: API Baileys Local (Recomendado para desenvolvimento)

### Pré-requisitos:
- Node.js instalado
- Porta 3000 disponível

### Instalação:

```bash
# 1. Clonar repositório da API Baileys
git clone https://github.com/WhiskeySockets/Baileys.git
cd Baileys

# 2. Instalar dependências
npm install

# 3. Criar servidor simples (arquivo server.js)
```

### Código do servidor (server.js):

```javascript
const { default: makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const express = require('express');
const app = express();

app.use(express.json());

let sock;
let qr = '';

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    
    sock = makeWASocket({
        auth: state,
        printQRInTerminal: true
    });

    sock.ev.on('creds.update', saveCreds);
    
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr: qrCode } = update;
        
        if (qrCode) {
            qr = qrCode;
        }
        
        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        }
    });
}

// Endpoints
app.get('/status', (req, res) => {
    res.json({
        connected: sock?.user ? true : false,
        session: sock?.user?.id || 'none',
        qr_available: qr !== ''
    });
});

app.get('/qr', (req, res) => {
    if (qr) {
        res.json({ qr: qr });
        qr = ''; // Reset QR after sending
    } else {
        res.status(404).json({ error: 'QR code not available' });
    }
});

app.post('/send-message', async (req, res) => {
    const { number, message } = req.body;
    
    if (!sock?.user) {
        return res.status(400).json({ success: false, error: 'WhatsApp not connected' });
    }
    
    try {
        const jid = number.includes('@') ? number : `${number}@s.whatsapp.net`;
        const result = await sock.sendMessage(jid, { text: message });
        res.json({ success: true, messageId: result.key.id });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Iniciar servidor
connectToWhatsApp();
app.listen(3000, () => {
    console.log('Baileys API rodando na porta 3000');
});
```

### Para executar:

```bash
node server.js
```

## Opção 2: Docker (Mais fácil)

```bash
# Criar Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]

# Executar
docker build -t baileys-api .
docker run -p 3000:3000 baileys-api
```

## Opção 3: Usar API Externa

Existem serviços como:
- WhatsApp Business API (oficial, pago)
- APIs terceirizadas (varie preços e confiabilidade)

## Testando a Configuração

1. **Verificar se API está rodando:**
   ```bash
   curl http://localhost:3000/status
   ```

2. **No bot Telegram:**
   - Menu → WhatsApp/Baileys
   - Verificar Status (deve mostrar "API Online")
   - Gerar QR Code
   - Escanear com WhatsApp do celular

3. **Testar envio:**
   - Use "Teste de Envio" no menu do bot
   - Verifique se mensagem chegou no WhatsApp

## Solução de Problemas

### "API Baileys não está rodando"
- Certifique-se que o servidor Node.js está rodando na porta 3000
- Verifique se não há firewall bloqueando a porta
- Execute `netstat -an | grep 3000` para confirmar

### "QR Code não disponível"
- Reinicie o servidor da API
- WhatsApp pode já estar conectado
- Aguarde alguns segundos após iniciar a API

### "Erro ao enviar mensagem"
- Confirme que WhatsApp foi conectado via QR Code
- Verifique se o número do cliente está correto (+55...)
- Teste com seu próprio número primeiro

## Configuração de Produção

Para produção, considere:
- Usar PM2 para gerenciar o processo Node.js
- Configurar SSL/HTTPS
- Implementar rate limiting
- Backup das sessões de autenticação
- Monitoramento de logs

## Próximos Passos

Após configurar a API Baileys:
1. Teste a conexão no bot
2. Configure dados da empresa nas configurações
3. Faça testes de envio
4. Configure agendamentos automáticos
5. Use templates personalizados