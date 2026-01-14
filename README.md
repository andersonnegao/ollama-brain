# 🎥 Dossiê de Vídeos

Sistema inteligente para análise, transcrição e geração automática de dossiês de conteúdo de vídeos do YouTube.

## ✨ Características

- 📹 **Extração automática de transcrições** do YouTube
- 🎵 **Fallback com Whisper**: se não houver transcrição oficial, aceita upload de áudio
- 🧠 **Análise com Ollama**: processamento local com modelos de IA (Mistral, Llama, etc)
- 📋 **Dossiê estruturado em Markdown**: resumo executivo, afirmações verificáveis, pessoas citadas, etc
- 🔐 **Segurança**: autenticação por Bearer token + CORS controlado
- 🎨 **UI moderna**: React/Vite + design escuro responsivo
- ⚡ **Rápido**: processamento local, sem dependências externas

## 🚀 Quick Start (Local)

### Pré-requisitos

- Docker & Docker Compose (recomendado)
- Ou: Python 3.11+, Node.js 18+, FFmpeg, Ollama

### Com Docker Compose (easiest)

```bash
# 1. Clone o repositório
git clone https://github.com/yourusername/ollama-brain.git
cd ollama-brain

# 2. Crie arquivo .env (copie do .env.example)
cp .env.example .env

# 3. Suba os containers (Ollama + FastAPI)
docker-compose up -d

# 4. Em outro terminal, instale e rode o frontend
cd frontend
npm install
npm run dev

# 5. Acesse no navegador
# Frontend: http://localhost:3000
# API: http://localhost:8080
```

### Manualmente (sem Docker)

#### Backend

```bash
# 1. Instale Ollama
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Windows: https://ollama.ai/download

# 2. Inicie Ollama e puxe o modelo
ollama serve
# Em outro terminal:
ollama pull mistral:latest

# 3. Instale dependências Python
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Rode a API
export API_TOKEN="dev-token"
export OLLAMA_BASE_URL="http://127.0.0.1:11434"
python -m uvicorn api:app --host 0.0.0.0 --port 8080 --reload
```

#### Frontend

```bash
# Em outro terminal
cd frontend
npm install
npm run dev
# Acesse http://localhost:3000
```

## 📚 Estrutura do Projeto

```
ollama-brain/
├── backend/
│   ├── api.py              # FastAPI app
│   ├── requirements.txt    # Dependências Python
│   ├── Dockerfile         # Docker image
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # App principal
│   │   ├── App.css
│   │   ├── components/
│   │   │   ├── DossierForm.jsx
│   │   │   ├── DossierResult.jsx
│   │   │   └── TokenPrompt.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🔧 Configuração (ENV)

### Backend

```env
API_TOKEN=sua-senha-secreta-aqui
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=mistral:latest
WHISPER_MODEL=base
MAX_UPLOAD_SIZE=209715200    # 200MB
CORS_ORIGINS=http://localhost:3000
ENV=dev
PORT=8080
```

### Frontend

```env
VITE_API_BASE_URL=http://localhost:8080
```

## 📡 API Endpoints

### GET /health
Health check da API.

```bash
curl http://localhost:8080/health
```

### POST /dossier
Cria um dossiê a partir de uma URL do YouTube.

**Headers:**
```
Authorization: Bearer <API_TOKEN>
Content-Type: multipart/form-data
```

**Form Data:**
- `url` (string, obrigatório): URL do YouTube
- `audio` (file, opcional): MP3/M4A/WAV se não houver transcrição oficial

**Exemplo:**
```bash
curl -X POST http://localhost:8080/dossier \
  -H "Authorization: Bearer seu-token" \
  -F "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -F "audio=@seu_audio.mp3"
```

**Response:**
```json
{
  "markdown": "---\ntype: video\n...\n",
  "transcript": "Transcrição completa...",
  "meta": {
    "video_id": "dQw4w9WgXcQ",
    "used": "youtube",
    "generated_at": "2026-01-11T10:30:00.000Z",
    "model": "mistral:latest"
  }
}
```

## 🌍 Deploy

### Backend → Fly.io

```bash
# 1. Instale fly CLI
# https://fly.io/docs/getting-started/installing-flyctl/

# 2. Crie app no Fly.io
flyctl launch --name dossier-api

# 3. Configure secrets
flyctl secrets set API_TOKEN="sua-senha-segura"
flyctl secrets set CORS_ORIGINS="https://seu-site.netlify.app"

# 4. Configure volume para Ollama (opcional, salva modelos)
flyctl volumes create ollama-data --size 50

# 5. Deploy
flyctl deploy

# 6. Verifique status
flyctl status
```

### Frontend → Netlify

```bash
# 1. Build
cd frontend
npm run build

# 2. No Netlify:
#    - Deploy via Git (GitHub/GitLab)
#    - Build command: npm run build
#    - Publish directory: dist
#    - Env var: VITE_API_BASE_URL=https://seu-app.fly.dev

# 3. Ou deploy manual
npm i -g netlify-cli
netlify deploy --prod --dir=dist
```

## 🔐 Segurança

- **Autenticação**: Token Bearer na header `Authorization`
- **CORS**: Restrito ao domínio Netlify (configure via `CORS_ORIGINS`)
- **Upload**: Limite de tamanho (default 200MB)
- **Logs**: Apenas meta e erros, não loga áudio/transcrição completa
- **Rate limit**: Básico por IP (implemente conforme necessário)

## 📝 Exemplo de Uso

### Via Web UI

1. Abra http://localhost:3000
2. Digite seu token (encontre em `.env`)
3. Cole URL do YouTube: `https://www.youtube.com/watch?v=...`
4. (Opcional) Envie arquivo de áudio
5. Clique "Gerar Dossiê"
6. Copie o Markdown ou baixe `.md`

### Via API (curl)

```bash
TOKEN="seu-token-aqui"
URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

curl -X POST http://localhost:8080/dossier \
  -H "Authorization: Bearer $TOKEN" \
  -F "url=$URL" \
  | jq .markdown > output.md
```

## 🐛 Troubleshooting

### Erro: "Ollama service unavailable"
- Confirme que Ollama está rodando: `ollama serve`
- Verifique URL: `curl http://127.0.0.1:11434/api/tags`

### Erro: "No transcript found"
- O vídeo pode não ter transcrição oficial no YouTube
- Solução: envie um arquivo de áudio (MP3, M4A, WAV)

### Erro: "Token invalid"
- Verifique o `API_TOKEN` em `.env`
- No frontend, o token é salvo em `localStorage`

### Lentidão
- Whisper é pesado: espere ~2 min para áudio de 1h
- Ollama depende de CPU/RAM: aumente recursos ou troque modelo
- Modelos recomendados por performance: `phi3:latest`, `mistral:7b`, `llama3.1:8b-instruct`

## 🤝 Contribuindo

1. Fork o repo
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m "Add: minha feature"`
4. Push: `git push origin feature/minha-feature`
5. Abra PR

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes

## 📞 Suporte

- Issues: [GitHub Issues](https://github.com/yourusername/ollama-brain/issues)
- Discussões: [GitHub Discussions](https://github.com/yourusername/ollama-brain/discussions)

---

**Feito com ❤️ por Anderson**
