# Deploy em produção — VPS Ubuntu (Hostinger)

Este guia assume uma VPS Ubuntu onde você já hospeda outros apps (Nginx já
instalado). A ideia é manter a pegada da aplicação mínima: **o servidor não
precisa ter Node.js instalado** — o build do frontend é feito na sua máquina e
só o resultado (`backend/static/`) vai para a VPS, junto com o backend Python.

## 1. Build local do frontend

Na sua máquina (não na VPS):

```
cd frontend
npm install
npm run build
```

Isso gera `backend/static/` com os arquivos prontos — o `backend/` já fica
completo e autossuficiente para copiar para o servidor.

## 2. Preparar a VPS

Prerequisitos (instale o que faltar):

```bash
sudo apt update
sudo apt install -y python3 python3-venv nginx certbot python3-certbot-nginx
```

Crie um usuário de sistema dedicado ao app (não rode como root nem com seu
usuário pessoal):

```bash
sudo useradd --system --create-home --shell /usr/sbin/nologin confra
sudo mkdir -p /opt/confra
sudo chown confra:confra /opt/confra
```

## 3. Copiar os arquivos

Da sua máquina, envie a pasta `backend/` (já com `static/` dentro) para a VPS:

```bash
rsync -avz --exclude '.venv' --exclude 'data' --exclude 'uploads' \
  backend/ usuario@seu-ip-vps:/opt/confra/backend/
```

(`data/` e `uploads/` ficam de fora porque são gerados no próprio servidor —
não faz sentido subir o banco/comprovantes de teste local.)

## 4. Ambiente virtual e dependências

Na VPS:

```bash
cd /opt/confra/backend
sudo -u confra python3 -m venv .venv
sudo -u confra .venv/bin/pip install -r requirements.txt
sudo mkdir -p data uploads
sudo chown -R confra:confra /opt/confra
```

## 5. Configurar o `.env` de produção

```bash
sudo -u confra cp .env.example .env
sudo -u confra nano .env
```

Preencha com valores reais e definitivos:

- `SECRET_KEY`: gere um valor forte e único —
  `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
- `ADMIN_USERNAME` / `ADMIN_PASSWORD`: credenciais reais da equipe de aprovação
  (senha forte — troque o placeholder).
- `CHECKIN_USERNAME` / `CHECKIN_PASSWORD`: credenciais reais da equipe de
  check-in.
- `PUBLIC_BASE_URL`: o domínio final com `https://`, ex.
  `https://confra.seudominio.com.br` (usado no link de reenvio de comprovante
  enviado por e-mail e liberado no CORS).
- `SMTP_*`: já usamos as credenciais reais da SEAD (`mail.goias.gov.br`).
- `EVENTO_VALOR_INSCRICAO`: valor exibido na página.

**Importante:** se você já rodou a aplicação localmente com um `SECRET_KEY` de
teste, gere um novo para produção — ele assina os tokens de login e os links
de reenvio de comprovante.

## 6. Serviço systemd

Copie o arquivo de exemplo e ajuste usuário/caminho se você usou outro:

```bash
sudo cp deploy/confra.service /etc/systemd/system/confra.service
sudo systemctl daemon-reload
sudo systemctl enable --now confra
sudo systemctl status confra
```

Ver logs em tempo real: `sudo journalctl -u confra -f`

O Uvicorn escuta só em `127.0.0.1:33269` (porta alta e incomum, escolhida para
não colidir com os outros apps já hospedados nesta VPS — confira antes com
`sudo ss -tlnp | grep 33269`; se já estiver em uso, troque o número em
`deploy/confra.service` e `deploy/nginx.conf.example` para outra porta livre).
Ela não fica exposta direto à internet — quem recebe tráfego externo é o Nginx.

## 7. Nginx + HTTPS

Copie `deploy/nginx.conf.example` para `/etc/nginx/sites-available/confra`,
troque `confra.seudominio.com.br` pelo domínio real, habilite e emita o
certificado:

```bash
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/confra
sudo nano /etc/nginx/sites-available/confra   # ajustar server_name
sudo ln -s /etc/nginx/sites-available/confra /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d confra.seudominio.com.br
```

O Certbot reescreve o arquivo automaticamente adicionando o bloco HTTPS e o
redirecionamento de HTTP para HTTPS, além de configurar a renovação automática.

## 8. Checar

```bash
curl -s https://confra.seudominio.com.br/api/health
# {"status":"ok"}
```

Depois teste pelo navegador: formulário de inscrição, login do admin
(`/admin/login`) e do check-in (`/checkin/login`).

## 9. Backup

Os únicos dados que importam preservar são `backend/data/confra.db` (banco) e
`backend/uploads/` (comprovantes). Um cron simples de backup diário:

```bash
sudo crontab -u confra -e
```

```
0 3 * * * tar -czf /opt/confra/backups/confra-$(date +\%F).tar.gz -C /opt/confra/backend data uploads
```

(crie a pasta `sudo -u confra mkdir -p /opt/confra/backups` antes.)

## 10. Atualizando depois de mudanças no código

1. Local: `cd frontend && npm run build` (atualiza `backend/static/`).
2. `rsync -avz --exclude '.venv' --exclude 'data' --exclude 'uploads' backend/ usuario@ip:/opt/confra/backend/`
3. Na VPS, se mudou `requirements.txt`: `sudo -u confra .venv/bin/pip install -r requirements.txt`
4. `sudo systemctl restart confra`
