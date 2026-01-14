# 📡 API Reference - Dossiê de Vídeos

Complete API documentation for integration and usage.

---

## 🎯 Base URL

**Development:** `http://localhost:8080`  
**Production:** `https://dossier-api.fly.dev`

---

## 🔐 Authentication

All endpoints (except `/health` optional) require Bearer token:

```bash
Authorization: Bearer <API_TOKEN>
```

**Example:**
```bash
curl -H "Authorization: Bearer seu-token-aqui" http://localhost:8080/health
```

---

## 📋 Endpoints

### 1. GET /health

Health check endpoint. No authentication required (but supported).

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:8080
```

**Response (200):**
```json
{
  "status": "ok",
  "timestamp": "2026-01-11T10:30:00.000Z",
  "ollama_model": "mistral:latest"
}
```

**Usage:**
```bash
curl http://localhost:8080/health
```

---

### 2. POST /dossier

Generate dossier from video URL. Requires Bearer token.

**Request:**
```http
POST /dossier HTTP/1.1
Host: localhost:8080
Authorization: Bearer <API_TOKEN>
Content-Type: multipart/form-data

Form data:
- url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
- audio: (optional) file.mp3
```

**Form Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `url` | string | ✅ Yes | YouTube URL or video ID |
| `audio` | file | ❌ No | MP3, M4A, or WAV file (max 200MB) |

**Success Response (200):**
```json
{
  "markdown": "---\ntype: video\nurl: https://www.youtube.com/watch?v=dQw4w9WgXcQ\nvideo_id: dQw4w9WgXcQ\ngenerated_at: 2026-01-11T10:30:00.000Z\n---\n\n# 🎥 Dossiê do vídeo\n\n## 🧠 Resumo executivo\n- Ponto 1\n- Ponto 2\n...",
  "transcript": "Texto completo da transcrição...",
  "meta": {
    "video_id": "dQw4w9WgXcQ",
    "used": "youtube",
    "generated_at": "2026-01-11T10:30:00.000Z",
    "model": "mistral:latest"
  }
}
```

**Error Response (422) - No transcript & no audio:**
```json
{
  "detail": "No official transcript found. Please upload an audio file (MP3, M4A, or WAV) and try again."
}
```

**Error Response (401) - Invalid token:**
```json
{
  "detail": "Invalid token"
}
```

**Error Response (413) - File too large:**
```json
{
  "detail": "File too large. Max size: 200MB"
}
```

**Error Response (500) - Server error:**
```json
{
  "detail": "Internal server error"
}
```

---

## 📝 Usage Examples

### Example 1: Generate dossier (official transcript)

```bash
curl -X POST http://localhost:8080/dossier \
  -H "Authorization: Bearer seu-token" \
  -F "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Example 2: Upload audio (fallback)

```bash
curl -X POST http://localhost:8080/dossier \
  -H "Authorization: Bearer seu-token" \
  -F "url=https://www.youtube.com/watch?v=VIDEO_ID" \
  -F "audio=@/path/to/audio.mp3"
```

### Example 3: Save result to file

```bash
curl -X POST http://localhost:8080/dossier \
  -H "Authorization: Bearer seu-token" \
  -F "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  | jq .markdown > output.md
```

### Example 4: JavaScript/Fetch

```javascript
const apiToken = "seu-token";
const videoUrl = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

const formData = new FormData();
formData.append("url", videoUrl);
// Opcionalmente: formData.append("audio", audioFile);

const response = await fetch("https://dossier-api.fly.dev/dossier", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${apiToken}`
  },
  body: formData
});

const data = await response.json();
console.log(data.markdown);  // Dossiê em Markdown
console.log(data.transcript); // Transcrição bruta
console.log(data.meta);       // Metadados
```

### Example 5: Python requests

```python
import requests

API_TOKEN = "seu-token"
API_URL = "https://dossier-api.fly.dev/dossier"
VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

files = {
    "url": (None, VIDEO_URL),
    # Opcionalmente:
    # "audio": open("audio.mp3", "rb")
}

response = requests.post(API_URL, headers=headers, files=files)
data = response.json()

print(data["markdown"])   # Dossiê
print(data["transcript"]) # Transcrição
print(data["meta"])       # Meta
```

---

## 🔄 Response Format

### Success Response

```typescript
{
  markdown: string,     // Dossiê completo em Markdown
  transcript: string,   // Transcrição bruta do vídeo
  meta: {
    video_id: string,   // YouTube video ID
    used: "youtube" | "whisper",  // Fonte da transcrição
    generated_at: string, // ISO timestamp
    model: string       // Ollama model used
  }
}
```

### Markdown Structure

```markdown
---
type: video
url: https://www.youtube.com/watch?v=...
video_id: xxx...
generated_at: 2026-01-11T10:30:00.000Z
---

# 🎥 Dossiê do vídeo

## 🧠 Resumo executivo (máx. 6 bullets)
- ...

## 📌 Afirmações verificáveis (lista)
- ...

## 🧍 Pessoas citadas (lista)
- ...

## 🏢 Empresas/organizações citadas (lista)
- ...

## 🧪 Vieses, exageros, lacunas
- ...

## 📚 Pistas de checagem
- ...

---

# 📝 Transcrição (bruta)

[Texto completo da transcrição]
```

---

## ⚙️ Configuration (Environment Variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `API_TOKEN` | `dev-token` | Bearer token for authentication |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama service URL |
| `OLLAMA_MODEL` | `mistral:latest` | Model for analysis |
| `WHISPER_MODEL` | `base` | Whisper model size |
| `MAX_UPLOAD_SIZE` | `209715200` | Max upload size (bytes, ~200MB) |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `ENV` | `dev` | Environment (dev/prod) |
| `PORT` | `8080` | API port |

---

## 🚦 Status Codes

| Code | Meaning | When |
|------|---------|------|
| `200` | OK | Request successful |
| `400` | Bad Request | Invalid URL or parameters |
| `401` | Unauthorized | Missing or invalid token |
| `413` | Payload Too Large | Upload exceeds 200MB |
| `422` | Unprocessable Entity | No transcript + no audio provided |
| `500` | Internal Error | Server error (Ollama down, etc) |
| `503` | Service Unavailable | Ollama not responding |

---

## 🔄 Rate Limiting

Recommended rate limits (not enforced in v1):
- **Per IP:** 10 requests/minute
- **Per token:** 100 requests/hour
- **Upload:** Max 200MB per file

---

## 📊 Performance

| Operation | Time |
|-----------|------|
| Health check | <50ms |
| Official transcript | 1-2s |
| Whisper transcription (1 min audio) | 30-60s |
| Ollama analysis | 1-3 min |
| **Total (full pipeline)** | **3-5 min** |

---

## 🐛 Common Errors & Solutions

### Error: "Invalid token"
```
Status: 401
Message: Invalid token

Solution:
1. Check API_TOKEN in flyctl secrets
2. Confirm token in Authorization header
3. Token format: Bearer <token>
```

### Error: "Ollama service unavailable"
```
Status: 503
Message: Ollama service unavailable

Solution:
1. Verify Ollama is running
2. Check OLLAMA_BASE_URL setting
3. Test: curl http://127.0.0.1:11434/api/tags
```

### Error: "No transcript found"
```
Status: 422
Message: No official transcript found...

Solution:
1. Video may not have official captions
2. Upload an audio file (MP3, M4A, WAV)
3. API will transcribe with Whisper
```

### Error: "File too large"
```
Status: 413
Message: File too large. Max size: 200MB

Solution:
1. Split audio into smaller chunks
2. Or increase MAX_UPLOAD_SIZE (requires redeploy)
```

---

## 🔒 Security Notes

✅ **HTTPS required** in production  
✅ **CORS configured** by domain  
✅ **Rate limiting recommended**  
✅ **Token expiration:** Implement in v2  
✅ **Audit logging:** Implement in v2  

---

## 📚 OpenAPI/Swagger

Interactive API docs available at:

- **Development:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc

Visit these URLs to test endpoints interactively!

---

## 🧪 Testing

### Test Health Endpoint

```bash
curl http://localhost:8080/health | jq
```

### Test with Video URL

```bash
TOKEN="dev-token"
URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

curl -X POST http://localhost:8080/dossier \
  -H "Authorization: Bearer $TOKEN" \
  -F "url=$URL" \
  | jq .meta
```

### Test with Audio Upload

```bash
TOKEN="dev-token"
URL="https://www.youtube.com/watch?v=VIDEO_ID"
AUDIO="./audio.mp3"

curl -X POST http://localhost:8080/dossier \
  -H "Authorization: Bearer $TOKEN" \
  -F "url=$URL" \
  -F "audio=@$AUDIO" \
  | jq .markdown > output.md
```

---

## 📖 Integration Guides

### Integration with Frontend

See `frontend/src/App.jsx` for complete React integration example.

### Integration with External Apps

1. Generate API token
2. Store securely (env var, secrets manager)
3. Make POST requests to `/dossier`
4. Parse JSON response
5. Use `markdown` field for display/export

### Webhook Integration (v2+)

Feature for future: callback when processing completes.

---

## 🔄 API Versioning

**Current:** v1.0.0  
**Stable:** Yes  
**Breaking changes:** None planned  

Future versions will maintain backward compatibility.

---

## 📞 Support

- **Docs:** README.md
- **Issues:** GitHub Issues
- **Questions:** GitHub Discussions

---

**Last updated:** 11 January 2026  
**Status:** ✅ Production Ready
