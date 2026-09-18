# Confraternização SEAD 2026 — Inscrições

Sistema de inscrição, aprovação de comprovante e check-in por QR Code para a
Confraternização de Fim de Ano da SEAD (18/12/2026, ASMEGO).

- **Backend**: FastAPI + SQLite (`backend/`)
- **Frontend**: Vue 3 + Tailwind CSS (`frontend/`)
- Sem Docker: o backend serve os arquivos estáticos do build do frontend diretamente
  (não precisa de Nginx nem containers).

Para testar manualmente o sistema (roteiro de testes, credenciais, páginas e
referência da API), veja **[GUIA_DE_TESTES.md](GUIA_DE_TESTES.md)**.

## Requisitos

- Python 3.12+
- Node.js 20+

## Configuração

```
cd backend
cp .env.example .env
```

Edite `backend/.env` com os valores reais: `SECRET_KEY`, credenciais de
`ADMIN_USERNAME/PASSWORD` e `CHECKIN_USERNAME/PASSWORD`, dados de `SMTP_*` e
`PUBLIC_BASE_URL` (URL pública onde o site vai rodar, usada no link de reenvio
de comprovante enviado por e-mail).

## Rodando em desenvolvimento

**Backend** (porta 33269 — escolhida alta e incomum de propósito, para não
colidir com outros apps que já rodam nesta máquina/servidor):

```
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload --port 33269
```

**Frontend** (porta 37230, com proxy de `/api` para o backend — já configurado
em `vite.config.js`):

```
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:37230`. O admin fica em `/admin/login` e o check-in em
`/checkin/login`.

## Deploy em produção

O deploy final é numa VPS Ubuntu (Hostinger), com Nginx na frente fazendo
HTTPS e um serviço `systemd` mantendo o backend no ar. Passo a passo completo,
com os arquivos de configuração prontos (`deploy/confra.service` e
`deploy/nginx.conf.example`), em **[DEPLOY.md](DEPLOY.md)**.

Resumo: o build do frontend é feito localmente (`npm run build`, sai em
`backend/static/`) e só o `backend/` — já autossuficiente, sem precisar de
Node no servidor — é copiado para a VPS.

## Testes automatizados (backend)

```
cd backend
.venv\Scripts\python -m pytest -q
```

Cobre: validação de CPF, geração/validação de token de QR Code, validação de
tipo/tamanho de arquivo enviado, e o fluxo completo de inscrição → rejeição →
reenvio de comprovante → aprovação → check-in (incluindo bloqueio de reuso do
QR Code).

## Personalização

- **Identidade visual**: o tema atual em [Home.vue](frontend/src/views/Home.vue)
  é um placeholder de fim de ano (cores em `frontend/tailwind.config.js`, seção
  `confra`). Troque textos, cores e a lista de atrações pelas informações reais
  do evento, e substitua o bloco "QR Code PIX" pela imagem real fornecida pela
  SEAD.
- **Unidades e Anexos de lotação**: gerenciados pela própria tela de admin
  (`/admin`, seção "Gerenciar unidades e anexos de lotação"). Os valores em
  [seed.py](backend/app/seed.py) são apenas para o banco não começar vazio.
