#!/usr/bin/env python3
"""
Script para iniciar containers e rodar o teste do pipeline
Aguarda de forma inteligente (verifica conectividade)
"""
import subprocess
import urllib.request
import json
import time
import sys

print("=" * 80)
print("🚀 INICIAR CONTAINERS E RODAR TESTE")
print("=" * 80)

# 1. Iniciar containers em background (sem esperar)
print("\n1️⃣ Iniciando containers (background)...")
subprocess.Popen(
    ['docker-compose', 'up', '-d'],
    cwd='/workspaces/ollama-brain',
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print("   ✅ Comando enviado")

# 2. Aguardar Ollama ficar pronto (com verificação periódica)
print("\n2️⃣ Aguardando Ollama ficar pronto (máx 10 min)...")
max_attempts = 120
for attempt in range(max_attempts):
    try:
        with urllib.request.urlopen(
            urllib.request.Request('http://localhost:11434/api/tags'),
            timeout=5
        ) as resp:
            data = json.loads(resp.read().decode())
            models = data.get('models', [])
            if models:
                print(f"   ✅ Ollama PRONTO com modelos: {[m['name'] for m in models]}")
                break
    except:
        pass
    
    if attempt % 6 == 0:  # Print a cada 30 segundos
        print(f"   ⏳ Tentativa {attempt + 1}/{max_attempts}... ({(attempt + 1) * 5}s)")
    time.sleep(5)
else:
    print("   ❌ Timeout! Ollama não ficou pronto")
    sys.exit(1)

# 3. Rodar teste
print("\n3️⃣ Enviando requisição /dossier...")
print("   Processando: audio.mp3 → Whisper → Ollama → Markdown")

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
print("   ⏳ Processando (vai levar 2-5 minutos)...\n")

try:
    with urllib.request.urlopen(req, timeout=600) as resp:
        elapsed = time.time() - start_time
        response_data = json.loads(resp.read().decode())
        
        print("\n" + "=" * 80)
        print(f"✅ SUCESSO! Status: 200")
        print(f"⏱️  Tempo total: {elapsed:.1f}s ({elapsed/60:.1f}min)")
        print("=" * 80)
        
        # Salvar e exibir resultado
        markdown = response_data.get('markdown', '')
        with open('/workspaces/ollama-brain/dossier_output.md', 'w') as f:
            f.write(markdown)
        
        print(f"\n📊 Resultados salvos:")
        print(f"   📄 Markdown: {len(markdown)} caracteres")
        print(f"   📝 Transcrição: {len(response_data.get('transcript', ''))} caracteres")
        print(f"   💾 Arquivo: /workspaces/ollama-brain/dossier_output.md")
        
        print(f"\n📋 PREVIEW DO MARKDOWN:")
        print("=" * 80)
        print(markdown[:3000])
        if len(markdown) > 3000:
            print(f"\n... [{len(markdown) - 3000} caracteres restantes]")
        print("\n" + "=" * 80)
        
except urllib.error.HTTPError as e:
    elapsed = time.time() - start_time
    print(f"\n❌ Erro HTTP {e.code}")
    try:
        print(f"Resposta: {e.read().decode()}")
    except:
        pass
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n❌ Erro: {e}")

print("\n✅ Teste finalizado!")
