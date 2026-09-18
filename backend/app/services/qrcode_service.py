import io
import secrets

import qrcode


def generate_token() -> str:
    return secrets.token_urlsafe(24)


def generate_qr_png_bytes(data: str) -> bytes:
    img = qrcode.make(data, box_size=10, border=2)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
