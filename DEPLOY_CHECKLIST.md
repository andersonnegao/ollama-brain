# 🎯 Seu Checklist de Deploy (Dono)

Use este checklist para acompanhar cada passo do deploy em produção.

---

## 📋 Fase 1: Preparação (Pre-Deploy)

### Conta & Credenciais
- [ ] Conta Fly.io criada (https://fly.io)
- [ ] Conta Netlify criada (https://netlify.com)
- [ ] GitHub conta ativa com repositório

### Segurança
- [ ] Token API gerado (32+ chars)
  - Comando: `openssl rand -base64 32`
  - Guardado em lugar seguro ✅
- [ ] Domínio Netlify definido (será fornecido)
  - Exemplo: `seu-projeto.netlify.app`

### Locais
- [ ] Código já está em GitHub
- [ ] Repositório é privado (se necessário)

---

## 🚀 Fase 2: Deploy Backend (Fly.io)

### 2.1 Preparar Fly.io

- [ ] `flyctl` instalado
- [ ] `flyctl auth login` executado
- [ ] Login confirmado (token salvo)

**Comando:**
```bash
flyctl auth login
# Abre navegador, faz login
```

### 2.2 Criar App

- [ ] App criado com `flyctl launch`
- [ ] Nome: `dossier-api`
- [ ] Região: escolhida (ex: `syd` = Sydney)
- [ ] Respondeu "n" para todas as DBs

**Comando:**
```bash
cd /seu/repo/ollama-brain
flyctl launch --name dossier-api --region syd
```

### 2.3 Configurar Secrets

- [ ] `API_TOKEN` secret definido
- [ ] `CORS_ORIGINS` secret definido

**Comandos:**
```bash
# Seu token gerado antes
flyctl secrets set API_TOKEN="seu-token-gerado-aqui"

# Seu domínio Netlify (será fornecido)
flyctl secrets set CORS_ORIGINS="https://seu-site.netlify.app"
```

### 2.4 Deploy

- [ ] `flyctl deploy` executado com sucesso
- [ ] Esperou ~5-10 min (primeira vez é lenta)
- [ ] Logs mostram "Ollama loaded" (ou similar)

**Comando:**
```bash
flyctl deploy

# Acompanhe em outro terminal:
flyctl logs --follow
```

### 2.5 Verificação

- [ ] URL do app copiada (ex: `https://dossier-api.fly.dev`)
- [ ] Health check respondendo 200
- [ ] Logs sem erros

**Testes:**
```bash
# Deve retornar JSON com "ok"
curl https://SEU_APP.fly.dev/health
```

---

## 🌐 Fase 3: Deploy Frontend (Netlify)

### 3.1 Preparar Git

- [ ] Código commitado e pusheado para GitHub
- [ ] Repositório visível em https://github.com/seu-usuario/seu-repo

**Comandos:**
```bash
git add .
git commit -m "Initial commit: Dossiê de Vídeos v1"
git push origin main
```

### 3.2 Conectar Netlify

- [ ] Entrado em https://app.netlify.com
- [ ] Clicado em "Add new site" → "Import an existing project"
- [ ] Autorizado Netlify no GitHub
- [ ] Repositório selecionado

### 3.3 Configurar Build

Na tela de deploy, confirmou:

- [ ] **Base directory:** `frontend`
- [ ] **Build command:** `npm run build`
- [ ] **Publish directory:** `frontend/dist`

### 3.4 Configurar Ambiente

- [ ] Clicado em **Advanced**
- [ ] Adicionada variável:
  - Nome: `VITE_API_BASE_URL`
  - Valor: `https://SEU_APP.fly.dev` (do Fly.io)

### 3.5 Deploy

- [ ] Clicado "Deploy site"
- [ ] Esperou ~3 minutos
- [ ] URL do site copiada (ex: `https://seu-projeto.netlify.app`)

---

## 🧪 Fase 4: Testes (Validação)

### 4.1 Teste de Acesso

- [ ] Abrou site no navegador: `https://seu-site.netlify.app`
- [ ] Página carregou sem erros
- [ ] Token prompt apareceu

### 4.2 Teste de Autenticação

- [ ] Digitou seu token (o gerado na Fase 2)
- [ ] Clicou "Acessar"
- [ ] Entrou na página principal

### 4.3 Teste 1: Vídeo com Transcrição

**Vídeo:** https://www.youtube.com/watch?v=dQw4w9WgXcQ

- [ ] Colou URL no campo
- [ ] **Não fez upload** de áudio
- [ ] Clicou "Gerar Dossiê"
- [ ] Dossiê foi gerado (esperou ~1-2 min)
- [ ] Viu aba "Dossiê" com conteúdo Markdown
- [ ] Viu aba "Transcrição" com texto

**✓ Esperado:** Dossiê gerado sem upload

### 4.4 Teste 2: Vídeo sem Transcrição

**Instrução:** Procure um vídeo sem legendas (difícil de achar, mas exista)

- [ ] Colou URL (video sem legendas)
- [ ] Clicou "Gerar Dossiê"
- [ ] Recebeu mensagem clara: 
  ```
  "Nenhuma transcrição encontrada. Envie um arquivo de áudio..."
  ```
- [ ] Upload field ficou visível
- [ ] Selecionou arquivo MP3 (áudio teste)
- [ ] Clicou novamente "Gerar Dossiê"
- [ ] Transcreveu com Whisper (esperou ~1-2 min)
- [ ] Gerou dossiê do áudio enviado

**✓ Esperado:** Fallback para Whisper funcionou

### 4.5 Teste 3: Funcionalidades

- [ ] Clicou **"Copiar Markdown"** → copiou corretamente
- [ ] Clicou **"Baixar .md"** → fez download do arquivo
- [ ] Clicou **"Baixar .txt"** (transcrição) → fez download

**✓ Esperado:** Todos os botões funcionam

### 4.6 Teste 4: Responsivo

- [ ] Abrou em **mobile** (devtools F12 → responsivo)
- [ ] Layout ajustou corretamente
- [ ] Botões ainda funcionam

**✓ Esperado:** Design responsivo OK

---

## ✅ Fase 5: Aceite Final

### Checklist de Aceite

- [ ] Site Netlify abre e carrega ✓
- [ ] Autenticação por token OK ✓
- [ ] URL → transcrição oficial → dossiê (sem áudio) ✓
- [ ] Mensagem clara quando falta transcrição ✓
- [ ] Upload áudio → Whisper → dossiê ✓
- [ ] Botão "Copiar Markdown" funciona ✓
- [ ] Botão "Baixar .md" funciona ✓
- [ ] Botão "Baixar .txt" funciona ✓
- [ ] Abas dossiê/transcrição funcionam ✓
- [ ] API `/health` OK ✓
- [ ] CORS sem erros ✓
- [ ] Design responsivo OK ✓

**Resultado: ✅ PRONTO PARA PRODUÇÃO**

---

## 🎓 Proximos Passos (Dia 0)

- [ ] Compartilhar link com equipe/stakeholders
- [ ] Testar com conteúdo real do seu domínio
- [ ] Recolher feedback
- [ ] Documentar issues encontrados

---

## 🆘 Problemas Comuns

### "API não responde"
```bash
flyctl status
flyctl logs --follow
# Aguarde ~5 min (primeiro boot é lento)
```

### "CORS error"
Significa que o `CORS_ORIGINS` está errado.
```bash
flyctl secrets set CORS_ORIGINS="https://seu-site.netlify.app"
flyctl deploy
# Aguarde redeploy
```

### "Token inválido"
Confirmou que está usando o token correto? Se não, regener:
```bash
flyctl secrets set API_TOKEN="novo-token-aqui"
flyctl deploy
```

### "Site carrega mas API não"
Espere mais. Primeiro boot do Ollama leva ~5-10 min.
```bash
# Acompanhe
flyctl logs --follow
```

---

## 📞 Quando Tudo Está OK

Se chegou aqui, você tem:

✅ API rodando em `https://dossier-api.fly.dev`
✅ Frontend rodando em `https://seu-site.netlify.app`
✅ Tudo funcionando end-to-end
✅ Sistema seguro (token + CORS)
✅ Pronto para uso!

---

## 📋 Rastreamento

**Status Geral:**
- [ ] Preparação: ________ 
- [ ] Backend: ________
- [ ] Frontend: ________
- [ ] Testes: ________
- [ ] Aceite: ✅ PRONTO

**Data de Conclusão:** ________

**Notas Adicionais:**
```
(deixar espaço para anotações)




```

---

**Boa sorte! 🚀**

Se travar em qualquer ponto, consulte:
- README.md (docs gerais)
- OWNER_SETUP.md (setup passo-a-passo)
- FLY_IO_DEPLOY.md (backend específico)
- NETLIFY_DEPLOY.md (frontend específico)

