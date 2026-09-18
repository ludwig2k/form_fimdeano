# Deploy em produção — VPS Ubuntu (Hostinger)

Este guia assume uma VPS Ubuntu onde você já hospeda outros apps (Nginx já
instalado). O código — incluindo o build do frontend já pronto em
`backend/static/` — vem do repositório
[github.com/ludwig2k/form_fimdeano](https://github.com/ludwig2k/form_fimdeano)
via `git clone`/`git pull`. **O servidor não precisa ter Node.js instalado**:
o build é feito e commitado na sua máquina antes do `git push`, então um
`git pull` na VPS já traz tudo pronto.

## 1. Preparar a VPS

Pré-requisitos (instale o que faltar):

```bash
sudo apt update
sudo apt install -y python3 python3-venv git nginx certbot python3-certbot-nginx
```

Crie um usuário de sistema dedicado ao app (não rode como root nem com seu
usuário pessoal):

```bash
sudo useradd --system --create-home --shell /usr/sbin/nologin confra
sudo mkdir -p /opt/confra
sudo chown confra:confra /opt/confra
```

## 2. Clonar o repositório

```bash
sudo -u confra git clone https://github.com/ludwig2k/form_fimdeano.git /opt/confra
```

Isso já cria `/opt/confra/backend` (com `static/`, o build do frontend, já
dentro) e `/opt/confra/frontend` com o código-fonte — só ficam de fora
`data/`, `uploads/`, `.venv/` e `.env`, que são gerados/configurados na
própria VPS (gitignored de propósito).

Se o repositório for privado, `git clone` por HTTPS vai pedir usuário/senha
(GitHub não aceita mais senha de conta, precisa de um
[personal access token](https://github.com/settings/tokens)) — ou, mais
prático para deploy automatizado, gere uma
[deploy key SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)
no repositório e clone via `git@github.com:ludwig2k/form_fimdeano.git`.

## 3. Ambiente virtual e dependências

Na VPS:

```bash
cd /opt/confra/backend
sudo -u confra python3 -m venv .venv
sudo -u confra .venv/bin/pip install -r requirements.txt
sudo -u confra mkdir -p data uploads
```

## 4. Configurar o `.env` de produção

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

## 5. Serviço systemd

Copie o arquivo de exemplo e ajuste usuário/caminho se você usou outro:

```bash
sudo cp /opt/confra/deploy/confra.service /etc/systemd/system/confra.service
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

## 6. Nginx + HTTPS

Copie `deploy/nginx.conf.example` para `/etc/nginx/sites-available/confra`,
troque `confra.seudominio.com.br` pelo domínio real, habilite e emita o
certificado:

```bash
sudo cp /opt/confra/deploy/nginx.conf.example /etc/nginx/sites-available/confra
sudo nano /etc/nginx/sites-available/confra   # ajustar server_name
sudo ln -s /etc/nginx/sites-available/confra /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d confra.seudominio.com.br
```

O Certbot reescreve o arquivo automaticamente adicionando o bloco HTTPS e o
redirecionamento de HTTP para HTTPS, além de configurar a renovação automática.

## 7. Checar

```bash
curl -s https://confra.seudominio.com.br/api/health
# {"status":"ok"}
```

Depois teste pelo navegador: formulário de inscrição, login do admin
(`/admin/login`) e do check-in (`/checkin/login`).

## 8. Backup

Os únicos dados que importam preservar são `backend/data/confra.db` (banco) e
`backend/uploads/` (comprovantes). Um cron simples de backup diário:

```bash
sudo crontab -u confra -e
```

```
0 3 * * * tar -czf /opt/confra/backups/confra-$(date +\%F).tar.gz -C /opt/confra/backend data uploads
```

(crie a pasta `sudo -u confra mkdir -p /opt/confra/backups` antes.)

## 9. Atualizando depois de mudanças no código

1. Local: se mudou algo no frontend, rode `cd frontend && npm run build`
   primeiro (isso atualiza `backend/static/`, que é versionado).
2. Local: `git add -A`, `git commit`, `git push`.
3. Na VPS: `cd /opt/confra && sudo -u confra git pull`
4. Se mudou `requirements.txt`: `sudo -u confra /opt/confra/backend/.venv/bin/pip install -r requirements.txt`
5. `sudo systemctl restart confra`
