import os, sys, time, re, json, textwrap, subprocess
from urllib.request import Request, urlopen
from urllib.error import URLError

# Optional deps:
# - youtube-transcript-api (recommended)
# - whisper (fallback if no transcript and you provide audio.mp3)
#
# You already installed whisper; we'll try transcript first.

VIDEO_ID_RE = re.compile(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\b|$)")

def extract_video_id(url: str) -> str:
    m = VIDEO_ID_RE.search(url)
    if not m:
        raise ValueError("Não consegui extrair o video_id do link. Cole um link padrão do YouTube.")
    return m.group(1)

def safe_slug(s: str) -> str:
    s = re.sub(r"[^0-9A-Za-z_-]+", "_", s.strip())
    return s[:80] if s else "video"

def http_post_json(url: str, payload: dict, timeout: int = 300) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def ollama_generate(prompt: str, model: str, base_url: str) -> str:
    # Ollama endpoint: POST /api/generate
    out = http_post_json(f"{base_url.rstrip('/')}/api/generate", {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }, timeout=600)
    return (out.get("response") or "").strip()

def chunk_text(text: str, max_chars: int = 9000) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        # try to break on sentence end
        cut = text.rfind(".", start, end)
        if cut == -1 or cut < start + int(max_chars * 0.6):
            cut = end
        else:
            cut = cut + 1
        chunks.append(text[start:cut].strip())
        start = cut
    return [c for c in chunks if c]

def try_youtube_transcript(video_id: str) -> str | None:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception:
        return None

    # Try Portuguese first, then English
    langs = ["pt", "pt-BR", "pt-PT", "en"]
    try:
        t = YouTubeTranscriptApi.get_transcript(video_id, languages=langs)
        return "\n".join([x["text"] for x in t]).strip()
    except Exception:
        return None

def whisper_transcribe(audio_path: str, model_name: str = "base") -> str:
    import whisper
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return (result.get("text") or "").strip()

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 video2dossie_pro.py <LINK_YOUTUBE> [pasta_saida]")
        sys.exit(1)

    url = sys.argv[1].strip()
    video_id = extract_video_id(url)
    out_dir = sys.argv[2].strip() if len(sys.argv) >= 3 else f"cases/{video_id}"
    os.makedirs(out_dir, exist_ok=True)

    transcript_path = os.path.join(out_dir, "transcript.txt")
    dossier_path = os.path.join(out_dir, "dossie.md")

    print(f"📌 Video ID: {video_id}")
    print(f"📁 Pasta do caso: {out_dir}")

    # 1) Try official transcript
    transcript = try_youtube_transcript(video_id)
    if transcript:
        print("✅ Transcrição oficial do YouTube encontrada.")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
    else:
        print("⚠️ Não consegui pegar transcrição oficial.")
        print("➡️ Agora preciso que você SUBA um arquivo de áudio como:")
        print(f"   {out_dir}/audio.mp3")
        print("")
        print("Como baixar no Mac (exemplo):")
        print('  yt-dlp -x --audio-format mp3 "SEU_LINK_AQUI" -o audio.%(ext)s')
        print("Depois, arraste o audio.mp3 para a pasta do caso no Codespace.")
        print("")
        audio_path = os.path.join(out_dir, "audio.mp3")
        # Wait for user to upload
        for i in range(720):  # up to 60 min (720*5s)
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1024 * 100:
                print("✅ audio.mp3 detectado. Transcrevendo com Whisper…")
                transcript = whisper_transcribe(audio_path, model_name=os.environ.get("WHISPER_MODEL", "base"))
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                break
            time.sleep(5)
            if i % 12 == 0:  # every 1 min
                print("… aguardando upload de audio.mp3 na pasta do caso …")
        else:
            print("⛔ Timeout esperando audio.mp3. Envie o arquivo e rode o script de novo.")
            sys.exit(2)

    # 2) Build dossier using Ollama
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    model = os.environ.get("OLLAMA_MODEL", "mistral:latest")

    print(f"🧠 Gerando dossiê com Ollama ({model})…")
    chunks = chunk_text(transcript, max_chars=9000)

    # First pass: summarize each chunk
    chunk_summaries = []
    for idx, c in enumerate(chunks, 1):
        prompt = f"""Você é um analista investigativo. Resuma o TRECHO {idx}/{len(chunks)} abaixo em bullets curtos, mantendo fatos, nomes e números.
TRECHO:
{c}
"""
        try:
            s = ollama_generate(prompt, model=model, base_url=base_url)
        except URLError as e:
            print("⛔ Erro chamando Ollama. Confirme se 'ollama serve' está rodando no Codespace.")
            raise
        chunk_summaries.append(s)

    joined = "\n\n".join([f"### Trecho {i}\n{chunk_summaries[i-1]}" for i in range(1, len(chunk_summaries)+1)])

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

    md = f"""---
type: video
url: {url}
video_id: {video_id}
generated_at: {time.strftime("%Y-%m-%d %H:%M:%S")}
---

# 🎥 Dossiê do vídeo

{dossier}

---

# 📝 Transcrição (bruta)

{textwrap.fill(transcript, width=100)}
"""

    with open(dossier_path, "w", encoding="utf-8") as f:
        f.write(md)

    print("✅ Pronto! Arquivos gerados:")
    print(" -", transcript_path)
    print(" -", dossier_path)
    print("")
    print("👉 Agora é só abrir o dossie.md e colar no Obsidian.")

if __name__ == "__main__":
    main()
