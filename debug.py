#!/usr/bin/env python3
import subprocess
import urllib.request
import json
import time

print("🔍 DEBUG - Verificando status\n")

# 1. Iniciar containers
print("1️⃣ Iniciando containers docker-compose...")
result = subprocess.run(
    ['docker-compose', 'up', '-d'],
    cwd='/workspaces/ollama-brain',
    capture_output=True,
    text=True,
    timeout=30
)
print(result.stdout if result.stdout else result.stderr[:200])
time.sleep(5)

# 2. Containers rodando
print("\n2️⃣ Status dos containers:")
result = subprocess.run(
    ['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'],
    capture_output=True,
    text=True
)
print(result.stdout)

# 3. Testar Backend
print("3️⃣ Testando Backend (localhost:8080):")
try:
    with urllib.request.urlopen(urllib.request.Request('http://localhost:8080/health'), timeout=5) as resp:
        data = json.loads(resp.read().decode())
        print(f"✅ OK: {data['status']}")
except Exception as e:
    print(f"❌ Erro: {e}")

# 4. Testar Ollama
print("\n4️⃣ Testando Ollama (localhost:11434):")
try:
    with urllib.request.urlopen(urllib.request.Request('http://localhost:11434/api/tags'), timeout=5) as resp:
        data = json.loads(resp.read().decode())
        models = [m['name'] for m in data.get('models', [])]
        if models:
            print(f"✅ OK com modelos: {models}")
        else:
            print("⚠️  Respondendo mas sem modelos (ainda carregando?)")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n✅ Debug finalizado!")
