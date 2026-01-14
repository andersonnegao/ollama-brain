# 🚀 Deploy Backend no Fly.io

Guia passo-a-passo para fazer deploy da API no Fly.io.

## Pré-requisitos

- Conta no [Fly.io](https://fly.io) (gratuita com créditos)
- [flyctl](https://fly.io/docs/hands-on/install-flyctl/) instalado
- Estar logado: `flyctl auth login`

## Step 1: Prepare o Dockerfile

O arquivo `backend/Dockerfile` já está pronto. Ele:
- Instala Ollama
- Instala dependências Python
- Inicia Ollama + FastAPI no boot

## Step 2: Crie o app no Fly.io

```bash
cd /workspaces/ollama-brain

flyctl launch \
  --name dossier-api \
  --region syd \
  --image-label latest
```

Responda as perguntas:
- **Would you like to set up a Postgresql database?** → N
- **Would you like to set up an Upstash Redis database?** → N
- **Would you like to set up a Tigris project?** → N

Isso vai gerar `fly.toml`.

## Step 3: Configure fly.toml

Edite `fly.toml` para adicionar variáveis de ambiente e volumes:

```toml
app = "dossier-api"
primary_region = "syd"

[build]
  dockerfile = "backend/Dockerfile"

[build.args]
  # (sem args necessários)

[env]
  OLLAMA_MODEL = "mistral:latest"
  WHISPER_MODEL = "base"
  ENV = "prod"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[http_service.checks]
  interval = "30s"
  timeout = "5s"
  grace_period = "40s"
  method = "get"
  path = "/health"

[[mounts]]
  source = "ollama_data"
  destination = "/root/.ollama"
  initial_size = "50gb"
  auto_extend_size_percent = 20
```

## Step 4: Crie o volume

```bash
flyctl volumes create ollama_data \
  --region syd \
  --size 50
```

Isso cria espaço de 50GB para guardar modelos Ollama.

## Step 5: Configure secrets

```bash
# Token da API (MUDE ISSO!)
flyctl secrets set \
  --app dossier-api \
  API_TOKEN="seu-token-super-secreto-aqui-32-chars-min"

# CORS (domínio do Netlify)
flyctl secrets set \
  --app dossier-api \
  CORS_ORIGINS="https://seu-site.netlify.app,https://www.seu-site.netlify.app"
```

Verifique os secrets:
```bash
flyctl secrets list --app dossier-api
```

## Step 6: Deploy

```bash
flyctl deploy --app dossier-api
```

Isso vai:
1. Build a imagem Docker
2. Enviar para Fly.io
3. Criar máquina (pode levar ~5 min)
4. Iniciar Ollama + FastAPI

**Primeira execução é lenta** (~5-10 min) pois:
- Compila tudo
- Baixa Ollama
- Pullza modelo Mistral

## Step 7: Verifique o status

```bash
# Status geral
flyctl status --app dossier-api

# Logs (últimas linhas)
flyctl logs --app dossier-api

# Ver todas as linhas (follow)
flyctl logs --app dossier-api --follow
```

## Step 8: Teste a API

```bash
# Health check
curl https://dossier-api.fly.dev/health

# Com token
TOKEN="seu-token-aqui"
curl -H "Authorization: Bearer $TOKEN" \
  https://dossier-api.fly.dev/health
```

## Step 9: Configure no Netlify (Frontend)

No dashboard do Netlify:

1. **Build settings:**
   - Build command: `npm run build`
   - Publish directory: `dist`

2. **Environment variables:**
   - Nome: `VITE_API_BASE_URL`
   - Valor: `https://dossier-api.fly.dev`

3. Trigger deploy

## 📋 Checklist

- [ ] `flyctl auth login` OK
- [ ] `flyctl launch` realizado
- [ ] `fly.toml` editado com volumes e healthcheck
- [ ] Volume `ollama_data` criado
- [ ] `API_TOKEN` secret configurado
- [ ] `CORS_ORIGINS` secret configurado
- [ ] `flyctl deploy` realizado com sucesso
- [ ] `/health` retorna 200 OK
- [ ] Frontend Netlify conectado à API

## 🔧 Troubleshooting

### Erro: "Error: Machine is out of memory"

O contêiner está usando muita RAM. Soluções:

1. Aumente a RAM da máquina:
   ```bash
   flyctl machines list --app dossier-api
   flyctl machines update <MACHINE_ID> --memory 8192  # 8GB
   ```

2. Ou troque o modelo para algo mais leve:
   ```bash
   flyctl secrets set \
     --app dossier-api \
     OLLAMA_MODEL="phi3:latest"
   ```

### Erro: "Connection refused" ao testar API

A máquina pode estar ainda inicializando. Espere 2-3 min:
```bash
flyctl logs --app dossier-api --follow
```

### Ollama demorando para carregar

Normal! Primeira vez leva tempo:
```bash
# Veja logs enquanto carrega
flyctl logs --app dossier-api --follow
```

### Erro: "Ollama service unavailable"

Confirme que Ollama iniciou:
```bash
flyctl exec --app dossier-api -- curl http://127.0.0.1:11434/api/tags
```

## 🎛️ Escalabilidade

Para suportar mais usuários simultâneos:

```bash
# Aumente mínimo de máquinas
flyctl scale count --app dossier-api 2

# Aumente auto-scaling
flyctl autoscale set --min 1 --max 3 --app dossier-api
```

## 💰 Custos estimados

- **Máquina shared-cpu-2x (padrão)**: ~$0.0007/h ≈ $5/mês
- **Volume 50GB**: ~$0.15/GB/mês ≈ $7.50/mês
- **Outbound data**: primeiros 3GB/mês free, depois $0.02/GB

**Total estimado: ~$12-15/mês** para setup básico.

## 🔄 Update & Redeploy

Para fazer deploy de atualizações:

```bash
# Edite código
# Commit e push para main

# Deploy
flyctl deploy --app dossier-api

# Acompanhe
flyctl logs --app dossier-api --follow
```

---

Pronto! Sua API está rodando em produção! 🎉
