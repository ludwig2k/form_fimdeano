# Guia de Testes — Confraternização SEAD 2026

Este documento é para quem vai testar manualmente o sistema de inscrição e
check-in da Confraternização de Fim de Ano da SEAD (18/12/2026, ASMEGO), antes
de liberar para os servidores em geral.

## O que o sistema faz

- Página pública com informações do evento e formulário de inscrição.
- Upload do comprovante de pagamento (imagem ou PDF).
- Conferência manual do comprovante por uma equipe (aprovar/rejeitar).
- Se rejeitado, o servidor recebe e-mail com o motivo e um link para reenviar
  o comprovante (sem precisar preencher tudo de novo).
- Se aprovado, o servidor recebe por e-mail um QR Code de entrada.
- Tela de check-in para a recepção validar o QR Code (por câmera ou digitando
  o código manualmente) e liberar a entrada — cada QR só pode ser usado uma
  vez.

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Backend / API | Python + [FastAPI](https://fastapi.tiangolo.com/) |
| Banco de dados | SQLite (arquivo único, sem servidor de banco separado) |
| Frontend | [Vue 3](https://vuejs.org/) + [Tailwind CSS](https://tailwindcss.com/) |
| Autenticação (admin/check-in) | Tokens JWT |
| Geração de QR Code | biblioteca Python `qrcode` |
| Leitura de QR Code (câmera) | biblioteca JS `html5-qrcode` |
| Envio de e-mail | SMTP institucional (`mail.goias.gov.br`) |

## Onde acessar

Peça a URL do ambiente de testes a quem configurou (local, ou já na VPS). A
estrutura de páginas é a mesma nos dois casos, só muda o endereço base.

## Perfis e páginas

| Perfil | Página | O que faz |
|---|---|---|
| Servidor (público) | `/` | Landing do evento + formulário de inscrição |
| Servidor (público) | `/sucesso/:id` | Tela de confirmação após enviar a inscrição |
| Servidor (público) | `/reenvio/:token` | Reenviar comprovante (link vem por e-mail em caso de rejeição) |
| Equipe de aprovação | `/admin/login` | Login do painel administrativo |
| Equipe de aprovação | `/admin` | Lista de inscrições, aprovar/rejeitar/excluir, gerenciar unidades e anexos |
| Equipe de check-in | `/checkin/login` | Login da tela de check-in |
| Equipe de check-in | `/checkin` | Leitor de QR Code (câmera ou código manual) |

## Credenciais de teste

Peça a quem configurou o ambiente as credenciais de `admin` e `checkin`
(estão no arquivo `backend/.env`, campos `ADMIN_USERNAME`/`ADMIN_PASSWORD` e
`CHECKIN_USERNAME`/`CHECKIN_PASSWORD`).

## Roteiro sugerido de testes

1. **Inscrição válida**: acesse `/`, preencha nome, CPF (real e válido —
   o sistema confere o dígito verificador), e-mail, unidade e anexo de
   lotação, anexe um comprovante (imagem ou PDF, até 5MB). Deve cair na tela
   de sucesso com o número da inscrição.
2. **Validações do formulário**:
   - CPF inválido (ex: `111.111.111-11`) → deve recusar com mensagem de erro.
   - Arquivo de tipo não suportado (ex: `.txt`, `.docx`) → deve recusar.
   - Arquivo maior que 5MB → deve recusar.
   - CPF repetido → deve avisar que já existe inscrição com aquele CPF.
3. **Aprovação**: entre em `/admin/login`, veja a inscrição em "Pendentes",
   clique em "Ver comprovante" (confere se abre certo) e depois "Aprovar".
   Confirme que chegou e-mail no endereço usado na inscrição, com o QR Code
   de entrada e o código em texto.
4. **Rejeição e reenvio**: crie outra inscrição de teste, rejeite pelo admin
   informando um motivo. Confira que chega e-mail com o motivo e um link.
   Abra o link (`/reenvio/:token`), envie um novo comprovante e confirme que
   a inscrição volta para "Pendentes" no admin.
5. **Check-in**: aprove uma inscrição de teste, entre em `/checkin/login` e
   depois `/checkin`. Teste os dois caminhos:
   - Câmera: aponte para o QR Code recebido por e-mail (em outra tela/celular).
   - Manual: cole/digite o código de texto que veio no e-mail, caso a câmera
     não esteja disponível.
   Deve mostrar nome, unidade e anexo, e liberar a entrada.
6. **Bloqueio de reuso**: tente validar o mesmo QR Code/código de novo — deve
   recusar avisando que já foi utilizado, mostrando a hora do check-in
   anterior.
7. **Exclusão**: no admin, exclua uma inscrição de teste e confirme que ela
   some da lista.
8. **Unidades e Anexos**: no admin, abra "Gerenciar unidades e anexos de
   lotação", adicione um item novo e confirme que ele aparece no formulário
   de inscrição (`/`). Desative um item e confirme que ele some das opções
   do formulário (mas inscrições antigas que já usavam ele continuam
   normais).

## Referência rápida da API

Todas as rotas começam com `/api`. As de admin/check-in exigem um token
(`Authorization: Bearer ...`) obtido no login.

| Método | Rota | Quem usa | O que faz |
|---|---|---|---|
| GET | `/api/health` | — | Health check (`{"status":"ok"}`) |
| GET | `/api/unidades` | Público | Lista unidades de lotação ativas |
| GET | `/api/anexos` | Público | Lista anexos de lotação ativos |
| POST | `/api/inscricoes` | Público | Cria uma inscrição (multipart, com o arquivo do comprovante) |
| GET | `/api/inscricoes/reenvio/{token}` | Público | Consulta status/motivo de uma inscrição rejeitada |
| POST | `/api/inscricoes/reenvio/{token}` | Público | Reenvia o comprovante e volta a inscrição para pendente |
| POST | `/api/admin/login` | Admin | Login, retorna token |
| GET | `/api/admin/inscricoes` | Admin | Lista inscrições (filtro opcional por status) |
| GET | `/api/admin/inscricoes/{id}/comprovante` | Admin | Baixa/visualiza o arquivo do comprovante |
| POST | `/api/admin/inscricoes/{id}/aprovar` | Admin | Aprova e dispara e-mail com QR Code |
| POST | `/api/admin/inscricoes/{id}/rejeitar` | Admin | Rejeita (com motivo) e dispara e-mail com link de reenvio |
| DELETE | `/api/admin/inscricoes/{id}` | Admin | Exclui a inscrição e o comprovante salvo |
| GET/POST/PATCH | `/api/admin/unidades`, `/api/admin/anexos` | Admin | CRUD das listas dos menus suspensos |
| POST | `/api/checkin/login` | Check-in | Login, retorna token |
| POST | `/api/checkin/validar` | Check-in | Valida um código de QR e marca a presença |

## Limitações conhecidas neste momento (ainda a ajustar)

- **Identidade visual**: o tema da página (cores, textos) ainda é um
  placeholder de fim de ano — vai ser substituído pela identidade visual
  real do evento.
- **QR Code de pagamento**: hoje é um espaço reservado na página — falta
  colocar a imagem real do PIX fornecida pela SEAD.
- **Unidades e Anexos**: os itens que já vêm cadastrados são só exemplo —
  a lista oficial deve ser cadastrada pela tela de admin antes de divulgar
  para os servidores.

## Como reportar um problema encontrado

Ao encontrar algo errado, informe: qual página/ação, o que era esperado, o
que aconteceu de fato, e se possível um print de tela. Isso agiliza bastante
a correção.
