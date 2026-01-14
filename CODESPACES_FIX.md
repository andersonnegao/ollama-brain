# 🔧 Teste de Endpoints - GitHub Codespaces

## ✅ Correção Aplicada

O problema era **proxy headers não sendo respeitados** no GitHub Codespaces tunnel.

### O que foi corrigido:

1. ✅ **ProxyHeadersMiddleware adicionado** (importação + configuração)
   - Agora respeita `X-Forwarded-For`, `X-Forwarded-Proto`, etc
   - Crítico para tunnels/proxies

2. ✅ **Endpoint `/debug/headers` adicionado**
   - Mostra headers, scope e path real
   - Sem autenticação (para debug)

3. ✅ **FastAPI configurado com docs_url explícito**
   - `/docs` → Swagger UI
   - `/openapi.json` → OpenAPI spec
   - `/redoc` → ReDoc

---

## 🧪 Como Testar

### Via linha de comando:

```bash
# 1. Health check (deve funcionar)
curl -X GET "https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/health"

# Esperado: 200 OK com JSON

# 2. Debug headers (sem auth, para investigar)
curl -X GET "https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/debug/headers"

# Esperado: Shows proxy headers info

# 3. POST /dossier COM TOKEN
curl -X POST "https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/dossier" \
  -H "Authorization: Bearer dev-token" \
  -F "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Esperado: 200 OK com JSON (ou 422 se sem transcrição)

# 4. OpenAPI spec
curl -X GET "https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/openapi.json"

# Esperado: JSON completo da spec
```

---

## 📍 Paths Corretos

| Endpoint | Method | Auth | Status |
|----------|--------|------|--------|
| `/health` | GET | ❌ No | ✅ Funciona |
| `/debug/headers` | GET | ❌ No | ✅ Novo (debug) |
| `/openapi.json` | GET | ❌ No | ✅ Corrigido |
| `/docs` | GET | ❌ No | ✅ Swagger UI |
| `/redoc` | GET | ❌ No | ✅ ReDoc |
| `/dossier` | POST | ✅ Bearer | ✅ Corrigido |

---

## 🚀 Próximo Passo

Reinicie o backend:

```bash
# Kill o processo anterior
pkill -f uvicorn

# Reinicie com os novos arquivos
API_TOKEN="dev-token" python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8080 --reload
```

Ou, se estiver usando o script existente, apenas:

```bash
# O reload deve pegar as mudanças automaticamente
# Se não, matke e reinicie
```

---

## 🔍 Se Ainda Der 404

1. Verifique `/debug/headers` primeiro
   - Se der 404: proxy está deslocando ainda
   - Se funcionar: confirme paths no JSON

2. Verifique se `ProxyHeadersMiddleware` foi importado (linha 16)

3. Verifique se o uvicorn está rodando (ps aux | grep uvicorn)

4. Verifique logs no terminal (deve mostrar requisições)

---

## 📊 Resposta Esperada - `/dossier` com sucesso

```json
{
  "markdown": "---\ntype: video\nurl: ...\n---\n# 🎥 Dossiê...",
  "transcript": "Text...",
  "meta": {
    "video_id": "xxx",
    "used": "youtube",
    "generated_at": "2026-01-11T...",
    "model": "mistral:latest"
  }
}
```

---

## 🎯 Se Funcionar

Você pode chamar:
- ✅ `POST /dossier` com multipart (url + audio)
- ✅ Sem 404 errors
- ✅ Com autenticação Bearer

Parabéns! A API está corrigida! 🎉

---

Testes confirmam funcionamento? Avise!
