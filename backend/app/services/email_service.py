import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..config import settings


def _send(to_email: str, subject: str, html_body: str, inline_images: dict[str, bytes] | None = None) -> None:
    if not settings.smtp_host:
        print(f"[email_service] SMTP não configurado. E-mail para {to_email} não enviado.")
        print(f"[email_service] Assunto: {subject}")
        print(f"[email_service] Corpo:\n{html_body}")
        return

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = settings.email_from
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    for content_id, image_bytes in (inline_images or {}).items():
        image = MIMEImage(image_bytes)
        image.add_header("Content-ID", f"<{content_id}>")
        image.add_header("Content-Disposition", "inline", filename=f"{content_id}.png")
        msg.attach(image)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.email_from, [to_email], msg.as_string())


def send_aprovacao_email(to_email: str, nome_completo: str, qr_token: str, qr_png_bytes: bytes) -> None:
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color:#8b1d24;">Inscrição confirmada!</h2>
      <p>Olá, {nome_completo}.</p>
      <p>Sua inscrição para a <strong>Confraternização de Fim de Ano da SEAD</strong>
      foi aprovada. Apresente o QR Code abaixo na entrada do evento:</p>
      <p style="text-align:center;"><img src="cid:qrcode" alt="QR Code de entrada" width="220" height="220" /></p>
      <p style="text-align:center; font-size:12px; color:#666;">
        Se a leitura do QR Code não funcionar na entrada, informe este código para a equipe:<br/>
        <code style="font-size:14px; background:#f5f5f5; padding:4px 8px; border-radius:4px; display:inline-block; margin-top:4px;">{qr_token}</code>
      </p>
      <p><strong>Data:</strong> 18/12/2026 (sexta-feira), das 16h às 22h<br/>
      <strong>Local:</strong> Salão de Eventos da ASMEGO — Rua 72 esquina com a BR-153,
      Jardim Goiás, Goiânia-GO</p>
      <p>Nos vemos lá!</p>
    </div>
    """
    _send(to_email, "Inscrição confirmada — Confraternização SEAD", html_body, {"qrcode": qr_png_bytes})


def send_rejeicao_email(to_email: str, nome_completo: str, motivo: str, reenvio_url: str) -> None:
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color:#8b1d24;">Comprovante não aprovado</h2>
      <p>Olá, {nome_completo}.</p>
      <p>O comprovante de pagamento enviado para a Confraternização de Fim de Ano da SEAD
      não pôde ser aprovado pelo seguinte motivo:</p>
      <p style="background:#f5f5f5; padding:12px; border-radius:6px;"><em>{motivo}</em></p>
      <p>Por favor, envie um novo comprovante através do link abaixo:</p>
      <p style="text-align:center;">
        <a href="{reenvio_url}" style="background:#8b1d24;color:#fff;padding:10px 18px;
        border-radius:6px;text-decoration:none;">Reenviar comprovante</a>
      </p>
    </div>
    """
    _send(to_email, "Comprovante não aprovado — Confraternização SEAD", html_body)
