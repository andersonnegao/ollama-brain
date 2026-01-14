# 🚀 Deploy Frontend no Netlify

Guia passo-a-passo para fazer deploy do frontend React no Netlify.

## Opção 1: Deploy via Git (Recomendado)

### Pré-requisitos

- Conta no [Netlify](https://netlify.com)
- Repositório no GitHub/GitLab/Bitbucket
- Código pusheado para `main` branch

### Passo 1: Conecte o repositório

1. Acesse [app.netlify.com](https://app.netlify.com)
2. Clique em **"Add new site"** → **"Import an existing project"**
3. Selecione seu repositório (GitHub/GitLab/Bitbucket)
4. Autorize o Netlify

### Passo 2: Configure o build

Na tela de configuração:

- **Base directory**: `frontend`
- **Build command**: `npm run build`
- **Publish directory**: `frontend/dist`

### Passo 3: Configure variáveis de ambiente

Clique em **"Advanced"** → **"New variable"**:

| Nome | Valor |
|------|-------|
| `VITE_API_BASE_URL` | `https://dossier-api.fly.dev` |

### Passo 4: Deploy

Clique em **"Deploy site"**. Espere ~2-3 minutos.

Seu site estará em: `https://seu-site.netlify.app`

## Opção 2: Deploy via Netlify CLI

### Passo 1: Instale Netlify CLI

```bash
npm install -g netlify-cli
```

### Passo 2: Autentique

```bash
netlify login
```

Abre navegador para autenticação. Complete o fluxo.

### Passo 3: Build

```bash
cd /workspaces/ollama-brain/frontend
npm run build
```

### Passo 4: Deploy

```bash
netlify deploy --prod --dir=dist
```

Pronto! O site estará em produção.

### Verificar status

```bash
netlify status
netlify logs --tail
```

## Opção 3: Deploy Manual (Drag & Drop)

1. Acesse [app.netlify.com](https://app.netlify.com)
2. Clique **"New site"** → **"Deploy manually"**
3. Build localmente:
   ```bash
   cd frontend
   npm run build
   ```
4. Arraste a pasta `dist` para Netlify

## 🔧 Configuração de domínio customizado

1. Em Netlify dashboard: **Domain settings**
2. Clique **"Add custom domain"**
3. Digite seu domínio (ex: `dossier.seusite.com`)
4. Siga instruções para DNS
5. Aguarde validação (pode levar até 48h)

## 🔐 Configurar HTTPS

Netlify faz **automaticamente** com Let's Encrypt (free).

Forçar HTTPS:
1. **Site settings** → **Build & deploy** → **Domain management**
2. Ativar **"Force HTTPS"**

## 📝 Variáveis de ambiente (.env)

No Netlify, variáveis sensíveis podem ser configuradas em:

1. **Site settings** → **Build & deploy** → **Environment**
2. Adicione variáveis conforme necessário

**OBS**: Token da API (se usado no frontend) é visível no navegador. Para v1 privada, use prompt na UI.

## 🔄 Updates & Redeploy

### Com Git (automático)

Qualquer push para `main` faz deploy automático!

```bash
# Edite código
git add .
git commit -m "Feature: melhoria na UI"
git push origin main

# Netlify constrói e deploya automaticamente
```

Acompanhe em: **Netlify dashboard** → **Deploys**

### Manual

```bash
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

## 📋 Checklist Deploy

- [ ] Repositório criado e sincronizado
- [ ] Conta Netlify criada
- [ ] Repositório conectado ao Netlify
- [ ] Build command: `npm run build`
- [ ] Publish directory: `frontend/dist`
- [ ] `VITE_API_BASE_URL` configurada
- [ ] Deploy realizado com sucesso
- [ ] Site acessível em `https://seu-site.netlify.app`
- [ ] Token armazenado localmente (localStorage)
- [ ] API respondendo normalmente

## 🧪 Teste o Frontend

```bash
# Localmente (antes de deploy)
cd frontend
npm run dev
# Acesse http://localhost:3000
```

Teste:
1. ✓ Digita token
2. ✓ Cola URL do YouTube
3. ✓ Clica "Gerar Dossiê"
4. ✓ Vê resultado com abas
5. ✓ Copia/baixa Markdown

## 🐛 Troubleshooting

### "API_BASE_URL undefined"

Verifique:
1. Variável `VITE_API_BASE_URL` configurada no Netlify
2. Build feito com `npm run build` (não `npm run dev`)
3. Valor correto: `https://dossier-api.fly.dev`

### Build falha

Verifique logs:
1. Netlify dashboard → **Deploys** → clique no build
2. Veja erro exato
3. Comandos comuns:
   ```bash
   # Limpa cache
   npm cache clean --force
   npm install
   npm run build
   ```

### Erro CORS

Se vir erro "Access to XMLHttpRequest blocked by CORS":

1. Verifique `CORS_ORIGINS` no backend:
   ```bash
   flyctl secrets list --app dossier-api
   ```

2. Atualize se necessário:
   ```bash
   flyctl secrets set \
     --app dossier-api \
     CORS_ORIGINS="https://seu-site.netlify.app"
   ```

3. Redeploy backend:
   ```bash
   flyctl deploy --app dossier-api
   ```

## 📊 Monitorar performance

Netlify fornece analytics grátis:
1. Dashboard → **Analytics**
2. Veja requisições, performance, erros

## 🚀 Otimizações (opcional)

### Gzip compression
Automático no Netlify ✓

### Cache headers
Edite `netlify.toml` na raiz:

```toml
[[headers]]
  for = "/*"
  [headers.values]
    Cache-Control = "public, max-age=3600"

[[headers]]
  for = "/api/*"
  [headers.values]
    Cache-Control = "no-cache"
```

### Redirects
Edite `netlify.toml`:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

Pronto! Seu frontend está online! 🎉
