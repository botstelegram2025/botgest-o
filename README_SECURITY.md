# Hardening & Isolamento — Bot Telegram + Baileys

Este pacote aplica melhorias de **segurança**, **isolamento** e **confiabilidade**:

## Principais mudanças
- **Rate limiting** (Flask-Limiter) e **verificação de secret** no `POST /webhook` do Telegram.
- **Endpoint `/healthz`** para health checks.
- **Execução via Gunicorn** (`start.sh`) — produção estável.
- **Dependências pinadas** em `requirements.txt`.
- **Novas proteções no Baileys** (`helmet`, `express-rate-limit`, **CORS whitelist** e **token por header**).
- **.env.example** com todas as variáveis de ambiente necessárias.
- **.gitignore** para evitar vazar segredos e arquivos de sessão.
- **Dockerfiles separados** para **isolamento** em dois serviços (`docker/Dockerfile.python` e `docker/Dockerfile.node`).

## Variáveis de ambiente
Veja `.env.example` e configure em produção:
- `TELEGRAM_WEBHOOK_SECRET` **obrigatório** em produção (env no provedor) — o Telegram envia no header `X-Telegram-Bot-Api-Secret-Token`.
- `SESSION_API_TOKEN` obrigatório para proteger a API do Baileys.
- `ALLOWED_ORIGINS` lista de domínios permitidos a consumir a API do Baileys.
- `WHATSAPP_API_BASE` URL pública do serviço Baileys (ex.: `https://<subdominio>.railway.app`).

## Deploy recomendado (Railway)
Crie **dois serviços**:
1. **bot-python** (Flask): use `docker/Dockerfile.python`. Defina `PORT=5000` (Railway fornece), `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `WHATSAPP_API_BASE` (apontando para o segundo serviço), etc.
2. **baileys-node**: use `docker/Dockerfile.node`. Defina `SESSION_API_TOKEN` e `ALLOWED_ORIGINS`. **Não** versione diretório `auth_info_default` — use volume/persistência.

Após subir, aponte o webhook do Telegram para `https://SEU_BOT_URL/webhook` e configure o **secret** correspondente.

## Notas de compatibilidade
- O Procfile foi simplificado para iniciar somente o Flask via Gunicorn. O serviço Node deve rodar separado (isolamento).
- Se você dependia de executar tudo no mesmo contêiner, use `docker-compose` localmente para desenvolvimento.

## Segurança adicional (opcional)
- Ativar HTTPS/Reverse Proxy com HSTS e TLS forte.
- Rotacionar tokens regularmente.
- Política de logs estruturados (JSON) e storage seguro.
