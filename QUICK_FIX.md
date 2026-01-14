# ⚡ AÇÃO IMEDIATA - GitHub Codespaces 404 Fix

## 🎯 Resumo Executivo

**Problema:** `/dossier` retornava 404 externamente  
**Causa:** Proxy headers não eram respeitados  
**Solução:** Adicionado `ProxyHeadersMiddleware`  
**Status:** ✅ Corrigido em `backend/api.py`

---

## 🚀 O que Fazer Agora

### 1️⃣ Reiniciar o Backend

```bash
# Terminal 1: Parar uvicorn
pkill -f uvicorn
sleep 2

# Reiniciar
cd /workspaces/ollama-brain
API_TOKEN="dev-token" python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8080 --reload
```

### 2️⃣ Testar Rapidinho

**Opção A: Script automático**
```bash
# Terminal 2: Rodar testes
bash test-codespaces.sh https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev
```

**Opção B: Manual (copy-paste)**
```bash
# Test 1: Health
curl https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/health

# Test 2: Debug headers
curl https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/debug/headers

# Test 3: Dossier com token
curl -X POST https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/dossier \
  -H "Authorization: Bearer dev-token" \
  -F "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 3️⃣ Validar Resultado

✅ **Se `/dossier` retornar:**
- Status 200 + JSON (sucesso)
- Status 422 + JSON (sem transcrição, precisa áudio)
- Status 401 + JSON (sem token)
- **Nunca mais 404** ✨

---

## 📝 O que Mudou

### `backend/api.py`

| Linha | Mudança |
|------|---------|
| 16 | ➕ `from fastapi.middleware.proxy_headers import ProxyHeadersMiddleware` |
| 183-189 | ✏️ FastAPI: `docs_url`, `openapi_url`, `redoc_url` explícitos |
| 194-198 | ➕ Middleware: `ProxyHeadersMiddleware(trusted_hosts=["*"])` |
| 215-235 | ✏️ `/health` e ➕ `/debug/headers` novos |

**Total:** ~15 linhas alteradas

---

## 🔍 Se Não Funcionar

1. **Verifique `/debug/headers`**
   ```bash
   curl https://<seu-codespace>-8080.app.github.dev/debug/headers | jq
   ```
   - Procure por headers `X-Forwarded-*`
   - Se ausentes: proxy não está passando

2. **Confirme uvicorn rodando**
   ```bash
   ps aux | grep uvicorn
   ```

3. **Verifique logs**
   - Terminal do VS Code deve mostrar requisições
   - Procure por erros Python

4. **Tente localhost primeiro**
   ```bash
   curl http://localhost:8080/dossier \
     -H "Authorization: Bearer dev-token" \
     -F "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   ```

---

## 📊 Path Final Correto

```
Não: /api/dossier
Não: /v1/dossier
✅ SIM: /dossier
```

**URL completa:**
```
POST https://<seu-codespace>-8080.app.github.dev/dossier
Authorization: Bearer dev-token
Content-Type: multipart/form-data

url=<youtube-url>
audio=<opcional>
```

---

## 📖 Documentação Completa

- 📄 [CODESPACES_FIX_SUMMARY.md](CODESPACES_FIX_SUMMARY.md) - Detalhes técnicos
- 📄 [CODESPACES_FIX.md](CODESPACES_FIX.md) - Instruções de teste
- 🧪 [test-codespaces.sh](test-codespaces.sh) - Script automático

---

## ✨ Próximo Passo

**1️⃣ Reiniciar backend** → **2️⃣ Testar** → **3️⃣ Celebrar** 🎉

```bash
# All-in-one (copy-paste):
pkill -f uvicorn; sleep 2; cd /workspaces/ollama-brain && API_TOKEN="dev-token" python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8080 --reload
```

Depois testa:
```bash
curl -X POST https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev/dossier \
  -H "Authorization: Bearer dev-token" \
  -F "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---

**Tudo certo? Me avisa!** ✅
