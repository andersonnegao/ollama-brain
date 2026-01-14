# 🚀 Quick Start (Desenvolvimento Local)

Rodando tudo em 5 minutos.

## Opção A: Com Docker Compose (Recommended ✨)

### Requisitos
- Docker + Docker Compose

### Comandos

```bash
# 1. Clone repo
git clone https://github.com/seu-repo/ollama-brain.git
cd ollama-brain

# 2. Copie .env
cp .env.example .env

# 3. Suba backend + Ollama
docker-compose up -d

# Aguarde ~5 min (Ollama carregando)
# Acompanhe:
docker-compose logs -f

# 4. Em novo terminal, rode frontend
cd frontend
npm install
npm run dev

# 5. Acesse
# Frontend: http://localhost:3000
# API: http://localhost:8080/health
```

**Token padrão:** `dev-token` (veja `.env`)

---

## Opção B: Manual (sem Docker)

### Requisitos
- Python 3.11+
- Node.js 18+
- FFmpeg
- Ollama

### Backend

```bash
# 1. Instale Ollama
# https://ollama.ai/download

# 2. Inicie Ollama (novo terminal)
ollama serve

# 3. Puxe modelo (outro terminal)
ollama pull mistral:latest

# 4. Setup Python
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Mac/Linux
# ou no Windows:
venv\Scripts\activate

pip install -r requirements.txt

# 5. Rode API
export API_TOKEN="dev-token"
export OLLAMA_BASE_URL="http://127.0.0.1:11434"
python -m uvicorn api:app --host 0.0.0.0 --port 8080 --reload

# Pronto! API em http://localhost:8080
```

### Frontend

```bash
# Em novo terminal
cd frontend
npm install
npm run dev

# Acesse http://localhost:3000
# Token: dev-token
```

---

## 🧪 Testes Rápidos

### Verificar Backend
```bash
curl http://localhost:8080/health
# Esperado: {"status": "ok", ...}
```

### Teste API com curl
```bash
TOKEN="dev-token"
URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

curl -X POST http://localhost:8080/dossier \
  -H "Authorization: Bearer $TOKEN" \
  -F "url=$URL"
```

### Verificar Frontend
1. Abra http://localhost:3000
2. Token: `dev-token`
3. URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
4. Clique "Gerar Dossiê"

---

## 🛠️ Desenvolvimento

### Alterar código

**Backend:**
- Edite `backend/api.py`
- API recarrega automaticamente (com `--reload`)

**Frontend:**
- Edite `frontend/src/**`
- Vite recarrega automaticamente

### Build para produção

```bash
# Frontend
cd frontend
npm run build
# Output: frontend/dist/

# Backend
# Docker:
docker build -t dossier-api -f backend/Dockerfile .
```

---

## 📝 Variáveis de Ambiente

Crie `.env` baseado em `.env.example`:

```env
API_TOKEN=dev-token
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=mistral:latest
WHISPER_MODEL=base
CORS_ORIGINS=*
ENV=dev
```

---

## 🧠 Como funciona (Pipeline)

1. **User coloca URL** → extrai `video_id`
2. **Tenta transcrição oficial** → youtube-transcript-api
3. **Se não houver:**
   - Pede upload de áudio (ou retorna erro 422)
   - Transcreve com Whisper
4. **Gera dossiê:**
   - Chunka transcrição (9k chars por chunk)
   - Summariza cada chunk com Ollama
   - Síntese final em Markdown estruturado
5. **Retorna JSON:**
   - `markdown`: dossiê pronto
   - `transcript`: texto bruto
   - `meta`: video_id, fonte, etc

---

## 🐛 Debug

### Logs Backend
```bash
# Docker
docker-compose logs -f api

# Manual
# Vê output do uvicorn em tempo real
```

### Logs Frontend
```bash
# No navegador
F12 → Console → vê erros
```

### Teste Ollama
```bash
# Verifique se Ollama está rodando
curl http://127.0.0.1:11434/api/tags

# Lista modelos instalados
ollama list
```

---

## 🔗 Links

- Backend API: http://localhost:8080
- Frontend: http://localhost:3000
- Ollama: http://127.0.0.1:11434
- Swagger (API docs): http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

---

## ❓ FAQ

**P: Como trocar o modelo Ollama?**
```bash
# Edite .env
OLLAMA_MODEL=phi3:latest
# Ou comandos de sistema
ollama pull phi3:latest
```

**P: Como resetar tudo?**
```bash
# Docker
docker-compose down -v

# Manual
rm -rf venv node_modules
```

**P: Whisper está lento. Como acelerar?**
```bash
# Use modelo menor
export WHISPER_MODEL=tiny
# Opções: tiny, base, small, medium, large
```

**P: Como logar na API?**
```bash
# Ver POST body, etc
# Use ferramentas: Postman, Insomnia, Bruno, etc
# Ou ativar verbose:
curl -v -X POST ...
```

---

Pronto para começar? 🚀

Dúvidas → Veja README.md ou abra Issue!
