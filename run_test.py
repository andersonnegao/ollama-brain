#!/usr/bin/env python3
"""
Teste do pipeline completo: Audio -> Whisper -> Ollama -> Markdown
"""
import subprocess
import urllib.request
import json
import time
import sys

print("=" * 80)
print("🚀 TESTE DO PIPELINE COMPLETO")
print("=" * 80)

# 1. Garantir containers rodando
print("\n1️⃣ Garantindo que os containers estão rodando...")
subprocess.run(
    ['docker-compose', 'up', '-d'],
    cwd='/workspaces/ollama-brain',
    capture_output=True
)
print("   ✅ Comando enviado")

# 2. Aguardar Ollama ficar pronto
print("\n2️⃣ Aguardando Ollama ficar pronto (máx 5 min)...")
for i in range(60):
    try:
        req = urllib.request.Request('http://localhost:11434/api/tags')
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get('models'):
                print(f"   ✅ Ollama PRONTO!")
                break
    except:
        if i % 6 == 0:
            print(f"   ⏳ Tentativa {i+1}/60...")
    time.sleep(5)
else:
    print("   ❌ Timeout!")
    sys.exit(1)

# 3. Fazer o teste
print("\n3️⃣ Enviando requisição /dossier...")
print("   Processando: audio.mp3 (13MB) -> Whisper -> Ollama -> Markdown")

url = "https://youtu.be/tKe1yDSwwnE"
token = "dev-token"
audio_path = "/workspaces/ollama-brain/audio.mp3"

with open(audio_path, 'rb') as f:
    audio_data = f.read()

# Multipart form data
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = []
body.append(f'--{boundary}'.encode())
body.append(b'Content-Disposition: form-data; name="url"')
body.append(b'')
body.append(url.encode())
body.append(f'--{boundary}'.encode())
body.append(b'Content-Disposition: form-data; name="audio"; filename="audio.mp3"')
body.append(b'Content-Type: audio/mpeg')
body.append(b'')
body.append(audio_data)
body.append(f'--{boundary}--'.encode())
body.append(b'')

body_bytes = b'\r\n'.join(body)

req = urllib.request.Request(
    'http://localhost:8080/dossier',
    data=body_bytes,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Authorization': f'Bearer {token}'
    }
)

start_time = time.time()

try:
    print("   ⏳ Processando (isso vai levar 1-3 minutos)...")
    with urllib.request.urlopen(req, timeout=600) as resp:
        elapsed = time.time() - start_time
        response_data = json.loads(resp.read().decode())
        
        print(f"\n✅ SUCESSO! Status: 200")
        print(f"⏱️  Tempo total: {elapsed:.1f}s ({elapsed/60:.1f}min)")
        
        # Salvar resultado
        markdown = response_data.get('markdown', '')
        with open('/workspaces/ollama-brain/dossier_output.md', 'w') as f:
            f.write(markdown)
        
        print(f"\n📊 Resultados:")
        print(f"   Markdown: {len(markdown)} caracteres")
        print(f"   Transcrição: {len(response_data.get('transcript', ''))} caracteres")
        print(f"   Arquivo salvo: /workspaces/ollama-brain/dossier_output.md")
        
        print(f"\n📄 PREVIEW DO MARKDOWN:")
        print("=" * 80)
        print(markdown[:2000])
        if len(markdown) > 2000:
            print(f"\n... [{len(markdown) - 2000} caracteres restantes]\n")
        print("=" * 80)
        
except urllib.error.HTTPError as e:
    elapsed = time.time() - start_time
    print(f"\n❌ ERRO HTTP {e.code}")
    print(f"Resposta: {e.read().decode()}")
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Teste finalizado!")
