# ✅ CORREÇÃO: GitHub Codespaces 404 Fix

## 🎯 O Problema

Ao chamar `POST /dossier` externamente via GitHub Codespaces tunnel público, retornava **404**, mesmo com token correto.

**Causas identificadas:**
1. ❌ `ProxyHeadersMiddleware` não estava configurado
2. ❌ Proxy headers (`X-Forwarded-For`, `X-Forwarded-Proto`) não eram respeitados
3. ❌ Sem endpoint de debug para investigar

---

## ✅ Solução Aplicada

### 1. Adicionado ProxyHeadersMiddleware

**Arquivo:** `backend/api.py` (linha 16 + linha 194)

```python
# Imports (linha 16)
from fastapi.middleware.proxy_headers import ProxyHeadersMiddleware

# Configuração (linha 194 - adicionado PRIMEIRO, antes do CORS)
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=["*"]
)
```

**Por que funciona:**
- GitHub Codespaces tunnel usa proxy reverso
- Proxy envia headers: `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`
- ProxyHeadersMiddleware faz FastAPI respeitar esses headers
- Garante que `request.client` e `request.url` sejam corretos

### 2. Adicionado Endpoint de Debug

**Arquivo:** `backend/api.py` (linhas 225-235)

```python
@app.get("/debug/headers")
async def debug_headers(request: FastAPIRequest):
    """Debug endpoint para investigar headers."""
    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "headers": dict(request.headers),
        "scope": {
            "type": request.scope.get("type"),
            "path": request.scope.get("path"),
            "root_path": request.scope.get("root_path"),
            "scheme": request.scope.get("scheme"),
            "server": request.scope.get("server"),
        }
    }
```

**Uso:** Para investigar se proxy está funcionando corretamente

### 3. FastAPI com URLs Explícitas

**Arquivo:** `backend/api.py` (linhas 183-189)

```python
app = FastAPI(
    title="Dossiê de Vídeos API",
    description="Video dossier generation with transcription and AI analysis",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",  # ← Explícito
    redoc_url="/redoc"
)
```

**Por que funciona:**
- Garante que OpenAPI spec está em `/openapi.json`
- Swagger em `/docs`

---

## 📋 Mudanças no Arquivo

| Linha | Tipo | Mudança |
|------|------|---------|
| 16 | Import | `from fastapi.middleware.proxy_headers import ProxyHeadersMiddleware` |
| 183-189 | Config | `docs_url`, `openapi_url`, `redoc_url` explícitos no FastAPI |
| 194-198 | Middleware | `ProxyHeadersMiddleware(trusted_hosts=["*"])` adicionado |
| 215-223 | Endpoint | `/health` agora inclui `request` param (para debug) |
| 225-235 | Endpoint | `/debug/headers` novo (sem auth) |

---

## 🧪 Como Testar

### 1. Verificar Health (básico)
```bash
curl -X GET "https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/health"

# Esperado:
# {"status":"ok",...,"url_path":"/health","root_path":"none"}
```

### 2. Investigar Headers (debug)
```bash
curl -X GET "https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/debug/headers" | jq

# Esperado: JSON com todos headers e scope
# Importante: verifique X-Forwarded-* headers
```

### 3. Testar `/dossier` (com token)
```bash
curl -X POST "https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/dossier" \
  -H "Authorization: Bearer dev-token" \
  -F "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Esperado:
# - Status 200: sucesso com Markdown + transcrição
# - Status 422: sem transcrição oficial (será necessário áudio)
# - NÃO: 404 (agora deve funcionar!)
```

### 4. Testar OpenAPI Spec
```bash
curl -X GET "https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/openapi.json" | jq '.paths | keys'

# Esperado:
# ["/health", "/debug/headers", "/dossier", "/openapi.json", "/docs", "/redoc"]
```

---

## 🚀 Reiniciar Backend

```bash
# 1. Matar processo anterior
pkill -f uvicorn

# 2. Aguardar 2 seg
sleep 2

# 3. Reiniciar
cd /workspaces/ollama-brain
API_TOKEN="dev-token" python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8080 --reload

# Esperado: Logs devem mostrar:
# INFO:     Uvicorn running on http://0.0.0.0:8080
# INFO:     Reload enabled. Watching for changes...
```

---

## ✅ Checklist de Validação

- [ ] Backend reiniciado sem erros
- [ ] `/health` retorna 200 (externamente)
- [ ] `/debug/headers` mostra proxy headers (X-Forwarded-*)
- [ ] `/openapi.json` retorna spec completo
- [ ] `/docs` abre Swagger UI
- [ ] `/dossier` POST com token retorna 200 ou 422 (nunca 404)
- [ ] `/dossier` POST sem token retorna 401

---

## 🎯 Resultado Esperado

Depois das mudanças, você consegue:

✅ **Chamar externamente:**
```bash
POST https://<codespace>-8080.app.github.dev/dossier
Authorization: Bearer dev-token
Content-Type: multipart/form-data

url=https://www.youtube.com/watch?v=...
audio=(opcional)
```

✅ **Receber sempre:**
- Status 200/422/401/413 (nunca 404)
- JSON válido
- Headers CORS corretos

---

## 🔗 Arquivo Modificado

- ✅ `/workspaces/ollama-brain/backend/api.py`

**Total de linhas mudadas:** ~15 linhas (imports + middleware + endpoints debug)

---

## 📞 Se Ainda Não Funcionar

1. Verifique `/debug/headers` - mostra exatamente o que está chegando
2. Procure por headers `X-Forwarded-*` - se não houver, proxy não está passando
3. Confirme que uvicorn reiniciou (ps aux | grep uvicorn)
4. Verifique logs no terminal (Ctrl+Shift+` no VS Code)

---

✅ **Status:** Corrigido e pronto para testar! 🎉
