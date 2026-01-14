#!/bin/bash
set -e

cd /workspaces/ollama-brain

echo "🚀 Iniciando containers..."
docker-compose up -d

echo "⏳ Aguardando 30 segundos para estabilizar..."
sleep 30

echo "✅ Containers iniciados!"
echo ""
docker-compose ps

echo ""
echo "🔍 Verificando Ollama..."
curl -s http://localhost:11434/api/tags | head -20 || echo "❌ Ollama ainda não respondendo"
