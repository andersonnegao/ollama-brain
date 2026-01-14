#!/usr/bin/env python3
"""
Teste do pipeline completo: Audio -> Whisper -> Ollama -> Markdown.
"""
import argparse
import json
import os
import time
import urllib.request
from pathlib import Path

def build_multipart(url: str, audio_bytes: bytes, boundary: str) -> bytes:
    body = [
        f"--{boundary}".encode(),
        b'Content-Disposition: form-data; name="url"',
        b"",
        url.encode(),
        f"--{boundary}".encode(),
        b'Content-Disposition: form-data; name="audio"; filename="audio.mp3"',
        b"Content-Type: audio/mpeg",
        b"",
        audio_bytes,
        f"--{boundary}--".encode(),
        b"",
    ]
    return b"\r\n".join(body)


def wait_for_api(base_url: str, timeout_s: int = 60) -> None:
    print("\n1️⃣ Checando se a API está no ar...")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            req = urllib.request.Request(f"{base_url.rstrip('/')}/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    print("   ✅ API respondeu /health")
                    return
        except Exception:
            time.sleep(2)
    raise RuntimeError("API não respondeu no tempo esperado. Inicie o FastAPI antes do teste.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Teste do pipeline completo: Audio -> Whisper -> Ollama -> Markdown."
    )
    parser.add_argument(
        "--api-base-url",
        default=os.environ.get("API_BASE_URL", "http://localhost:8080"),
        help="Base URL do FastAPI (ex: http://localhost:8080).",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("API_TOKEN", "dev-token"),
        help="Token Bearer para autenticação.",
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("TEST_VIDEO_URL", "https://youtu.be/tKe1yDSwwnE"),
        help="URL do vídeo do YouTube (campo obrigatório do endpoint).",
    )
    parser.add_argument(
        "--audio",
        default=os.environ.get("TEST_AUDIO_PATH"),
        help="Caminho para o arquivo de áudio (MP3).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    audio_path = Path(args.audio) if args.audio else repo_root / "audio.mp3"

    print("=" * 80)
    print("🚀 TESTE DO PIPELINE COMPLETO")
    print("=" * 80)

    wait_for_api(args.api_base_url)

    if not audio_path.exists():
        print(f"\n❌ Arquivo de áudio não encontrado: {audio_path}")
        return 1

    print("\n2️⃣ Enviando requisição /dossier...")
    print(f"   Processando: {audio_path.name} -> Whisper -> Ollama -> Markdown")

    audio_bytes = audio_path.read_bytes()
    boundary = "----OllamaBrainBoundary7MA4YWxkTrZu0gW"
    body_bytes = build_multipart(args.url, audio_bytes, boundary)

    req = urllib.request.Request(
        f"{args.api_base_url.rstrip('/')}/dossier",
        data=body_bytes,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {args.token}",
        },
    )

    start_time = time.time()
    try:
        print("   ⏳ Processando (isso pode levar alguns minutos)...")
        with urllib.request.urlopen(req, timeout=600) as resp:
            elapsed = time.time() - start_time
            response_data = json.loads(resp.read().decode())

            print("\n✅ SUCESSO! Status: 200")
            print(f"⏱️  Tempo total: {elapsed:.1f}s ({elapsed/60:.1f}min)")

            markdown = response_data.get("markdown", "")
            output_path = repo_root / "dossier_output.md"
            output_path.write_text(markdown, encoding="utf-8")

            print("\n📊 Resultados:")
            print(f"   Markdown: {len(markdown)} caracteres")
            print(f"   Transcrição: {len(response_data.get('transcript', ''))} caracteres")
            print(f"   Arquivo salvo: {output_path}")

            print("\n📄 PREVIEW DO MARKDOWN:")
            print("=" * 80)
            print(markdown[:2000])
            if len(markdown) > 2000:
                print(f"\n... [{len(markdown) - 2000} caracteres restantes]\n")
            print("=" * 80)
    except urllib.error.HTTPError as exc:
        elapsed = time.time() - start_time
        print(f"\n❌ ERRO HTTP {exc.code}")
        print(f"Tempo decorrido: {elapsed:.1f}s")
        print(f"Resposta: {exc.read().decode()}")
        return 1
    except Exception as exc:
        print(f"\n❌ ERRO: {exc}")
        return 1

    print("\n✅ Teste finalizado!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
