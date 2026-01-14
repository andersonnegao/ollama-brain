#!/bin/bash

# Script de teste para validar correção do GitHub Codespaces 404 fix

set -e

# Configuração
API_URL="${1:-https://musical-engine-7vrpwrx4qjqphpq9p-8080.app.github.dev}"
TOKEN="dev-token"
VIDEO_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

echo "🧪 Iniciando testes..."
echo "📍 API URL: $API_URL"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0

# Função auxiliar para testar
test_endpoint() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local auth=$4
    local data=$5
    
    test_count=$((test_count + 1))
    
    echo -n "[$test_count] $test_name... "
    
    # Construir comando curl
    local curl_cmd="curl -s -w '\n%{http_code}' -X $method"
    
    if [ "$auth" = "yes" ]; then
        curl_cmd="$curl_cmd -H 'Authorization: Bearer $TOKEN'"
    fi
    
    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -H 'Content-Type: multipart/form-data'"
        curl_cmd="$curl_cmd $data"
    fi
    
    curl_cmd="$curl_cmd '$API_URL$endpoint'"
    
    # Executar e capturar resposta
    response=$(eval "$curl_cmd")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    # Verificar status
    if [[ "$http_code" =~ ^(200|201|204|301|302|307|308)$ ]]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        pass_count=$((pass_count + 1))
        if [ "$6" = "verbose" ]; then
            echo "   Response: $body" | head -c 100
            echo ""
        fi
    else
        echo -e "${RED}❌ FAIL ($http_code)${NC}"
        echo "   Response: $body" | head -c 200
        echo ""
    fi
}

# Testes

echo "=== 1. ENDPOINTS SEM AUTENTICAÇÃO ==="
test_endpoint "Health check" "GET" "/health"
test_endpoint "Debug headers" "GET" "/debug/headers"
test_endpoint "OpenAPI spec" "GET" "/openapi.json"
test_endpoint "Swagger UI" "GET" "/docs"
test_endpoint "ReDoc" "GET" "/redoc"

echo ""
echo "=== 2. AUTENTICAÇÃO ==="
test_endpoint "Dossier SEM token (deveria 401)" "POST" "/dossier" "no" "-F 'url=$VIDEO_URL'"
test_endpoint "Dossier COM token" "POST" "/dossier" "yes" "-F 'url=$VIDEO_URL'"

echo ""
echo "=== 3. ERROS ==="
test_endpoint "Invalid video URL (400)" "POST" "/dossier" "yes" "-F 'url=invalid'"
test_endpoint "Endpoint inexistente (404)" "GET" "/inexistente"

echo ""
echo "=== RESULTADO ==="
echo -e "${GREEN}✅ Passed: $pass_count/$test_count${NC}"

if [ $pass_count -eq $test_count ]; then
    echo -e "${GREEN}🎉 Todos os testes passaram!${NC}"
    exit 0
else
    failed=$((test_count - pass_count))
    echo -e "${RED}⚠️  $failed testes falharam${NC}"
    exit 1
fi
