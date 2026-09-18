import os
import sys
import tempfile

import pytest

TEST_DIR = tempfile.mkdtemp(prefix="confra_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DIR}/test.db"
os.environ["UPLOAD_DIR"] = os.path.join(TEST_DIR, "uploads")
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin123"
os.environ["CHECKIN_USERNAME"] = "checkin"
os.environ["CHECKIN_PASSWORD"] = "checkin123"
os.environ["SECRET_KEY"] = "test-secret-key"
# Nunca usar o SMTP real do .env local nos testes: força o fallback de
# console (email_service._send apenas loga) para os testes ficarem rápidos,
# determinísticos e sem depender de rede.
os.environ["SMTP_HOST"] = ""

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.database import SessionLocal  # noqa: E402


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
