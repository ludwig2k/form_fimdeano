from app.services.qrcode_service import generate_qr_png_bytes, generate_token


def test_generate_token_is_unique_and_urlsafe():
    tokens = {generate_token() for _ in range(50)}
    assert len(tokens) == 50


def test_generate_qr_png_bytes_produces_valid_png():
    data = generate_qr_png_bytes("some-token-value")
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
