# 📋 Setup & Configuração (para o dono/usuário)

Guia final com checklist de tarefas para colocar o sistema em produção.

## 🎯 Pré-requisitos

Você precisa ter/fazer:

- [ ] Conta no Fly.io (criar em https://fly.io)
- [ ] Conta no Netlify (criar em https://netlify.com)
- [ ] Repositório no GitHub (com este projeto)
- [ ] Gerar uma **senha forte** para `API_TOKEN` (mínimo 32 caracteres)

## ⚙️ Passo 1: Preparar os segredos

### Gere um token seguro

```bash
# Opção 1: Linux/Mac
openssl rand -base64 32

# Opção 2: Qualquer lugar (online)
# Visite: https://www.random.org/strings/?num=1&len=32&digits=on&loweralpha=on&upperalpha=on
```

Guarde este token! Você vai usar em 2 lugares.

**Exemplo de token:**
```
aB3cDeFgHiJkLmNoPqRsTuVwXyZ1234+56=
```

## ⚙️ Passo 2: Deploy Backend (Fly.io)

### 2.1 Instale flyctl

- macOS: `brew install flyctl`
- Linux: `curl -L https://fly.io/install.sh | sh`
- Windows: https://fly.io/docs/hands-on/install-flyctl/

### 2.2 Faça login

```bash
flyctl auth login
```

Abre navegador, complete autenticação.

### 2.3 Configure e deploy

```bash
cd /workspaces/ollama-brain

# Crie o app
flyctl launch --name dossier-api --region syd

# Responda "n" para todas as bases de dados

# Configure o app
# (Copie conteúdo de fly.toml.template para fly.toml)

# Set secrets (USE SEU TOKEN!)
flyctl secrets set API_TOKEN="seu-token-gerado-aqui"
flyctl secrets set CORS_ORIGINS="https://seu-site.netlify.app"

# Deploy!
flyctl deploy
```

### 2.4 Verifique se rodou

```bash
# Status
flyctl status

# Logs (acompanhe loading do Ollama)
flyctl logs --follow

# Teste a API
curl https://dossier-api.fly.dev/health
```

**Esperado:** Status 200 OK com `{"status": "ok", ...}`

### 2.5 Copie a URL

Note a URL do seu app (ex: `https://dossier-api.fly.dev`).
Você vai usar em breve no Netlify.

---

## ⚙️ Passo 3: Deploy Frontend (Netlify)

### 3.1 Conecte GitHub ao Netlify

1. Acesse https://app.netlify.com
2. Clique **"Add new site"** → **"Import an existing project"**
3. Escolha GitHub
4. Autorize Netlify
5. Selecione seu repositório

### 3.2 Configure o build

Na tela de configuração:

| Campo | Valor |
|-------|-------|
| **Base directory** | `frontend` |
| **Build command** | `npm run build` |
| **Publish directory** | `frontend/dist` |

### 3.3 Configure ambiente

Clique **"Advanced"** → **"New variable"**:

| Nome | Valor |
|------|-------|
| `VITE_API_BASE_URL` | `https://dossier-api.fly.dev` |

### 3.4 Deploy

Clique **"Deploy site"**. Espere ~3 min.

Sua URL: `https://seu-nome.netlify.app`

### 3.5 Teste no navegador

1. Abra https://seu-nome.netlify.app
2. Cole seu token (o mesmo gerado no Passo 1)
3. Cola URL de um vídeo: `https://www.youtube.com/watch?v=...`
4. Clique "Gerar Dossiê"
5. Veja resultado! ✓

---

## 🧪 Passo 4: Teste com 3 vídeos

### Teste 1: Vídeo com transcrição oficial

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Esperado:**
- Sem upload de áudio
- Transcrição encontrada
- Dossiê gerado rapidamente

### Teste 2: Vídeo sem transcrição

Procure um vídeo sem legendas. Veja mensagem:
```
"Nenhuma transcrição encontrada. Envie um arquivo de áudio."
```

**Esperado:**
- Upload field aparece
- Selecione MP3/M4A/WAV
- Processa com Whisper (~1-2 min)
- Gera dossiê

### Teste 3: Podcast longo

Teste com um vídeo de 2+ horas.

**Esperado:**
- Demora mais (chunking + Ollama)
- Mas não timeout
- Resultado estruturado

---

## ✅ Checklist Final (Critérios de Aceite)

- [ ] Site Netlify abre e funciona
- [ ] Token funciona (não dá erro 401)
- [ ] Vídeo com transcrição gera dossiê sem áudio
- [ ] Vídeo sem transcrição mostra msg clara
- [ ] Upload de áudio gera transcrição
- [ ] Botão "Copiar Markdown" funciona
- [ ] Botão "Baixar .md" faz download
- [ ] Botão "Baixar .txt" (transcrição) funciona
- [ ] Abas "Dossiê" ↔ "Transcrição" funcionam
- [ ] API `/health` retorna 200 OK
- [ ] CORS funciona (sem erros no console)
- [ ] Design responsivo (mobile + desktop)

---

## 🔐 Segurança - Pontos Importantes

1. **API_TOKEN é sensível!**
   - Guardado em `flyctl secrets` (seguro)
   - Nunca versione no Git
   - Mude periodicamente se suspeitar compromisso

2. **CORS restrito**
   - Apenas seu domínio Netlify pode chamar API
   - Impeça uso por terceiros

3. **Logs não armazenam dados sensíveis**
   - Apenas meta + erros
   - Seu conteúdo não é logado

4. **HTTPS obrigatório**
   - Fly.io: automático
   - Netlify: automático
   - Token viaja criptografado

---

## 🆘 Troubleshooting Rápido

### "API indisponível"
```bash
flyctl status
flyctl logs --follow
```

### "Token inválido"
Confirme em:
```bash
flyctl secrets list
```

### "CORS error"
Atualize em Fly.io:
```bash
flyctl secrets set CORS_ORIGINS="https://seu-site.netlify.app"
flyctl deploy
```

### "Muito lento"
Normal! Primeira vez:
- Ollama carregando
- Modelo carregando
- Esperou ~5 min

Próximas requisições: mais rápidas

### "File too large"
Máximo 200MB. Divida áudio grande.

---

## 📞 Proximos passos (opcional)

- [ ] Configurar domínio customizado
- [ ] Adicionar Rate Limiting
- [ ] Implementar Job async (para podcasts longos)
- [ ] Adicionar cache de resultados
- [ ] Integração com Slack/Discord

---

## 📚 Links úteis

- Fly.io docs: https://fly.io/docs/
- Netlify docs: https://docs.netlify.com/
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Ollama: https://ollama.ai/

---

**Tudo pronto! Seu sistema está em produção! 🎉**

Dúvidas? Verifique os logs ou abra issue no GitHub.
