const { default: makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const express = require('express');
const QRCode = require('qrcode');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Middlewares
app.use(cors());
app.use(express.json());

// Estado global
let sock;
let qrCode = '';
let isConnected = false;
let connectionStatus = 'disconnected';

// Função para conectar ao WhatsApp
async function connectToWhatsApp() {
    try {
        console.log('🔄 Iniciando conexão com WhatsApp...');
        
        const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
        
        sock = makeWASocket({
            auth: state,
            printQRInTerminal: false
        });

        // Salvar credenciais
        sock.ev.on('creds.update', saveCreds);
        
        // Monitorar conexão
        sock.ev.on('connection.update', (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            console.log('📱 Status da conexão:', connection);
            
            if (qr) {
                console.log('📱 QR Code gerado!');
                qrCode = qr;
                connectionStatus = 'qr_ready';
            }
            
            if (connection === 'close') {
                isConnected = false;
                connectionStatus = 'disconnected';
                
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
                console.log('🔌 Conexão fechada. Reconectar?', shouldReconnect);
                console.log('🔍 Status code:', (lastDisconnect?.error)?.output?.statusCode);
                console.log('🔍 Disconnect reason:', DisconnectReason);
                
                // Se foi removido ou há conflito, limpar auth e permitir novo QR
                if ((lastDisconnect?.error)?.output?.statusCode === DisconnectReason.badSession ||
                    (lastDisconnect?.error)?.output?.statusCode === DisconnectReason.restartRequired ||
                    lastDisconnect?.error?.message?.includes('device_removed') ||
                    lastDisconnect?.error?.message?.includes('conflict')) {
                    console.log('🧹 Limpando sessão devido a conflito/remoção...');
                    qrCode = '';
                    connectionStatus = 'disconnected';
                    setTimeout(connectToWhatsApp, 2000);
                } else if (shouldReconnect) {
                    setTimeout(connectToWhatsApp, 3000);
                }
            } else if (connection === 'open') {
                isConnected = true;
                connectionStatus = 'connected';
                qrCode = '';
                console.log('✅ WhatsApp conectado!');
                console.log('📞 Número:', sock.user.id);
            } else if (connection === 'connecting') {
                connectionStatus = 'connecting';
                console.log('🔄 Conectando...');
            }
        });

    } catch (error) {
        console.error('❌ Erro ao conectar:', error);
        connectionStatus = 'error';
    }
}

// Endpoints da API

// Status da API
app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        status: connectionStatus,
        session: sock?.user?.id || null,
        qr_available: qrCode !== '',
        timestamp: new Date().toISOString()
    });
});

// Obter QR Code
app.get('/qr', async (req, res) => {
    try {
        if (!qrCode) {
            return res.status(404).json({ 
                success: false, 
                error: 'QR Code não disponível. Tente reconectar.' 
            });
        }

        // Gerar imagem QR Code
        const qrImage = await QRCode.toDataURL(qrCode);
        
        res.json({
            success: true,
            qr: qrCode,
            qr_image: qrImage,
            instructions: 'Abra WhatsApp → Configurações → Aparelhos conectados → Conectar um aparelho'
        });
        
    } catch (error) {
        console.error('❌ Erro ao gerar QR:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Erro ao gerar QR Code' 
        });
    }
});

// Enviar mensagem
app.post('/send-message', async (req, res) => {
    try {
        const { number, message } = req.body;
        
        if (!number || !message) {
            return res.status(400).json({
                success: false,
                error: 'Número e mensagem são obrigatórios'
            });
        }
        
        if (!isConnected) {
            return res.status(400).json({
                success: false,
                error: 'WhatsApp não conectado'
            });
        }
        
        // Formatar número
        const jid = number.includes('@') ? number : `${number}@s.whatsapp.net`;
        
        // Enviar mensagem
        const result = await sock.sendMessage(jid, { text: message });
        
        console.log('✅ Mensagem enviada:', number, message.substring(0, 50) + '...');
        
        res.json({
            success: true,
            messageId: result.key.id,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('❌ Erro ao enviar mensagem:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Reconectar
app.post('/reconnect', async (req, res) => {
    try {
        console.log('🔄 Reconectando...');
        qrCode = '';
        isConnected = false;
        connectionStatus = 'connecting';
        
        if (sock) {
            sock.end();
        }
        
        setTimeout(connectToWhatsApp, 1000);
        
        res.json({
            success: true,
            message: 'Reconexão iniciada'
        });
        
    } catch (error) {
        console.error('❌ Erro ao reconectar:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Limpar sessão
app.post('/clear-session', async (req, res) => {
    try {
        console.log('🧹 Limpando sessão...');
        
        if (sock) {
            sock.end();
        }
        
        // Limpar auth_info
        const fs = require('fs');
        const path = require('path');
        const authDir = './auth_info';
        
        if (fs.existsSync(authDir)) {
            const files = fs.readdirSync(authDir);
            for (const file of files) {
                fs.unlinkSync(path.join(authDir, file));
            }
        }
        
        qrCode = '';
        isConnected = false;
        connectionStatus = 'disconnected';
        
        // Reconectar após limpar
        setTimeout(connectToWhatsApp, 1000);
        
        res.json({ 
            success: true, 
            message: 'Sessão limpa e reconexão iniciada'
        });
        
    } catch (error) {
        console.error('❌ Erro ao limpar sessão:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Erro ao limpar sessão' 
        });
    }
});

// Health check
app.get('/', (req, res) => {
    res.json({
        service: 'Baileys API',
        status: 'running',
        connected: isConnected,
        timestamp: new Date().toISOString()
    });
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`🚀 Baileys API rodando na porta ${PORT}`);
    console.log(`📱 Status: http://localhost:${PORT}/status`);
    console.log(`🔗 QR Code: http://localhost:${PORT}/qr`);
    console.log('');
    
    // Conectar ao WhatsApp
    connectToWhatsApp();
});

// Tratamento de erros
process.on('uncaughtException', (error) => {
    console.error('❌ Erro não tratado:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Promise rejeitada:', reason);
});