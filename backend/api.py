import os
import re
import json
import tempfile
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Header, Request as FastAPIRequest
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIG FROM ENV
# ============================================================================
API_TOKEN = os.environ.get("API_TOKEN", "dev-token")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:latest")
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 200 * 1024 * 1024))  # 200MB

# ============================================================================
# SECURITY & UTILS
# ============================================================================

def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """Verify Bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    token = parts[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

# ============================================================================
# CORE LOGIC (from video2dossie_pro.py)
# ============================================================================

VIDEO_ID_RE = re.compile(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\b|$)")

def extract_video_id(url: str) -> str:
    """Extract video_id from YouTube URL."""
    m = VIDEO_ID_RE.search(url)
    if not m:
        raise ValueError("Could not extract video_id from link. Use standard YouTube URL.")
    return m.group(1)

def http_post_json(url: str, payload: dict, timeout: int = 300) -> dict:
    """POST JSON to endpoint."""
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def ollama_generate(prompt: str, model: str, base_url: str) -> str:
    """Call Ollama /api/generate endpoint."""
    try:
        out = http_post_json(f"{base_url.rstrip('/')}/api/generate", {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }, timeout=600)
        return (out.get("response") or "").strip()
    except URLError as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(status_code=503, detail="Ollama service unavailable")

def chunk_text(text: str, max_chars: int = 9000) -> list:
    """Split text into chunks."""
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        # Try to break on sentence end
        cut = text.rfind(".", start, end)
        if cut == -1 or cut < start + int(max_chars * 0.6):
            cut = end
        else:
            cut = cut + 1
        chunks.append(text[start:cut].strip())
        start = cut
    
    return [c for c in chunks if c]

def try_youtube_transcript(video_id: str) -> Optional[str]:
    """Try to fetch official transcript from YouTube."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception:
        logger.warning("youtube_transcript_api not installed")
        return None
    
    langs = ["pt", "pt-BR", "pt-PT", "en"]
    try:
        t = YouTubeTranscriptApi.get_transcript(video_id, languages=langs)
        return "\n".join([x["text"] for x in t]).strip()
    except Exception as e:
        logger.info(f"No transcript found for {video_id}: {e}")
        return None

def whisper_transcribe(audio_path: str, model_name: str = "base") -> str:
    """Transcribe audio using Whisper."""
    try:
        import whisper
    except Exception:
        raise HTTPException(status_code=500, detail="Whisper not installed")
    
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path)
        return (result.get("text") or "").strip()
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        raise HTTPException(status_code=500, detail="Whisper transcription failed")

def generate_dossier(transcript: str, model: str, base_url: str) -> str:
    """Generate dossier using Ollama."""
    chunks = chunk_text(transcript, max_chars=9000)
    
    # First pass: summarize each chunk
    chunk_summaries = []
    for idx, c in enumerate(chunks, 1):
        prompt = f"""Você é um analista investigativo. Resuma o TRECHO {idx}/{len(chunks)} abaixo em bullets curtos, mantendo fatos, nomes e números.
TRECHO:
{c}
"""
        s = ollama_generate(prompt, model=model, base_url=base_url)
        chunk_summaries.append(s)
    
    # Second pass: final synthesis
    joined = "\n\n".join([f"### Trecho {i}\n{chunk_summaries[i-1]}" for i in range(1, len(chunk_summaries) + 1)])
    
    final_prompt = f"""Você é um jornalista investigativo e analista de inteligência.

Com base nas notas por trecho abaixo, gere um DOSSIÊ do conteúdo.
IMPORTANTE:
- Se algo não estiver explícito nas notas, diga "não confirmado".
- Referências externas: sugira temas/fontes para checar (ex: "site do IBGE", "paper sobre X"), mas deixe claro que são sugestões de verificação.
- Seja objetivo, estruturado e útil para tomada de decisão.

NOTAS:
{joined}

Gere exatamente com estas seções em Markdown:

## 🧠 Resumo executivo (máx. 6 bullets)
## 📌 Afirmações verificáveis (lista)
## 🧍 Pessoas citadas (lista)
## 🏢 Empresas/organizações citadas (lista)
## 🧪 Vieses, exageros, lacunas (lista + 2 linhas explicando)
## 📚 Pistas de checagem (fontes/termos para pesquisar)
"""
    dossier = ollama_generate(final_prompt, model=model, base_url=base_url)
    return dossier

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Dossiê de Vídeos API",
    description="Video dossier generation with transcription and AI analysis",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health(request: FastAPIRequest):
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "ollama_model": OLLAMA_MODEL,
        "url_path": str(request.url.path),
        "root_path": request.scope.get("root_path", "none"),
    }

@app.get("/debug/headers")
async def debug_headers(request: FastAPIRequest):
    """Debug endpoint to see all headers (no auth required for debugging)."""
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

@app.post("/dossier")
async def create_dossier(
    url: str = Form(...),
    audio: Optional[UploadFile] = File(None),
    token: str = Depends(verify_token),
):
    """
    Create dossier from video URL and optional audio.
    
    - **url**: YouTube URL (required)
    - **audio**: MP3/M4A/WAV file (optional)
    - **Authorization**: Bearer <token> (required header)
    
    Returns JSON with markdown, transcript, and metadata.
    """
    try:
        # 1. Extract video_id
        video_id = extract_video_id(url)
        logger.info(f"Processing video: {video_id}")
        
        # 2. Try official transcript
        transcript = try_youtube_transcript(video_id)
        used_source = "youtube"
        
        # 3. If no transcript and no audio, return 422
        if not transcript and not audio:
            raise HTTPException(
                status_code=422,
                detail="No official transcript found. Please upload an audio file (MP3, M4A, or WAV) and try again."
            )
        
        # 4. If no transcript but audio provided, use Whisper
        if not transcript and audio:
            # Check file size
            contents = await audio.read()
            if len(contents) > MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {MAX_UPLOAD_SIZE // (1024*1024)}MB"
                )
            
            # Save to temp file and transcribe
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            
            try:
                transcript = whisper_transcribe(tmp_path, model_name=WHISPER_MODEL)
                used_source = "whisper"
                logger.info(f"Transcribed {len(transcript)} chars with Whisper")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        # 5. Generate dossier
        logger.info("Generating dossier with Ollama...")
        dossier = generate_dossier(transcript, model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        
        # 6. Build markdown response
        markdown = f"""---
type: video
url: {url}
video_id: {video_id}
generated_at: {datetime.utcnow().isoformat()}
---

# 🎥 Dossiê do vídeo

{dossier}

---

# 📝 Transcrição (bruta)

{transcript}
"""
        
        return {
            "markdown": markdown,
            "transcript": transcript,
            "meta": {
                "video_id": video_id,
                "used": used_source,
                "generated_at": datetime.utcnow().isoformat(),
                "model": OLLAMA_MODEL,
            }
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        reload=os.environ.get("ENV", "dev") == "dev"
    )
