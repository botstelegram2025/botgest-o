# Configuração WhatsApp/Baileys - Guia Rápido

## 1. Pré-requisitos

Para usar o sistema de envio de mensagens WhatsApp, você precisa:

- API Baileys rodando em `localhost:3000`
- Bot Telegram funcionando
- Pelo menos 1 cliente cadastrado no sistema

## 2. Como conectar o WhatsApp

### Pelo Bot Telegram:

1. Envie `/start` ou clique em **📱 WhatsApp/Baileys**
2. No menu WhatsApp, clique em **📱 Gerar QR Code**
3. Siga as instruções na tela:
   - Abra WhatsApp no celular
   - Vá em **Configurações** → **Aparelhos conectados**
   - Toque em **Conectar um aparelho**
   - Escaneie o QR Code gerado pelo bot

### Verificar conexão:
- Clique em **🔄 Verificar Status** para ver se conectou
- Status **🟢 Conectado** = pronto para envios
- Status **🟡 Aguardando QR Code** = precisa escanear QR
- Status **🔴 API Offline** = API Baileys não está rodando

## 3. Testar envios

1. No menu WhatsApp, clique em **🧪 Teste de Envio**
2. O bot enviará uma mensagem para o primeiro cliente cadastrado
3. Verifique se a mensagem chegou no WhatsApp do cliente
4. O resultado aparecerá no Telegram

## 4. Ver histórico

- **📋 Logs de Envio**: últimas 10 mensagens enviadas
- **📊 Estatísticas**: resumo de todos os envios

## 5. Configurações avançadas

No menu **⚙️ Configurações**:
- **🏢 Dados da Empresa**: nome e telefone da empresa
- **💳 Configurar PIX**: chave PIX e titular para cobranças
- **📱 Status WhatsApp**: URL da API e verificação

## 6. Solução de problemas

### QR Code não aparece:
- Verifique se API Baileys está rodando
- Reinicie a API se necessário

### Envios não funcionam:
- Confirme que WhatsApp está conectado (status 🟢)
- Verifique se o número do cliente está correto
- Teste com um número conhecido primeiro

### API Offline:
- Confirme que a API Baileys está em `localhost:3000`
- Verifique logs da API para erros
- Reinicie a API se necessário

## 7. Recursos automáticos

O sistema possui recursos de automação:
- **Agendamento**: mensagens automáticas de vencimento
- **Templates**: mensagens pré-configuradas
- **Fila**: processamento de mensagens em lote
- **Retry**: tentativas automáticas em caso de falha

## Próximos passos

Após conectar o WhatsApp:
1. Configure os dados da empresa no menu Configurações
2. Faça testes de envio para validar
3. Configure templates personalizados (em desenvolvimento)
4. Configure agendamentos automáticos de cobrança