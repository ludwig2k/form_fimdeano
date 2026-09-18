import io

from app import models

VALID_CPF = "111.444.777-35"
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00"
    b"\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _admin_token(client):
    resp = client.post("/api/admin/login", data={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _checkin_token(client):
    resp = client.post("/api/checkin/login", data={"username": "checkin", "password": "checkin123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _submit_inscricao(client, cpf=VALID_CPF, email="servidor@example.com"):
    unidades = client.get("/api/unidades").json()
    anexos = client.get("/api/anexos").json()
    files = {"comprovante": ("comprovante.png", io.BytesIO(PNG_BYTES), "image/png")}
    data = {
        "nome_completo": "Servidor de Teste",
        "cpf": cpf,
        "email": email,
        "unidade_id": str(unidades[0]["id"]),
        "anexo_id": str(anexos[0]["id"]),
    }
    return client.post("/api/inscricoes", data=data, files=files)


def test_seed_data_available(client):
    assert client.get("/api/unidades").json()
    assert client.get("/api/anexos").json()


def test_criar_inscricao_com_cpf_invalido_retorna_422(client):
    resp = _submit_inscricao(client, cpf="111.111.111-11", email="invalido@example.com")
    assert resp.status_code == 422


def test_admin_pode_excluir_inscricao(client):
    resp = _submit_inscricao(client, cpf="123.456.789-09", email="excluir@example.com")
    assert resp.status_code == 201
    inscricao_id = resp.json()["id"]

    admin_token = _admin_token(client)
    headers = {"Authorization": f"Bearer {admin_token}"}

    exclusao = client.delete(f"/api/admin/inscricoes/{inscricao_id}", headers=headers)
    assert exclusao.status_code == 204

    listagem = client.get("/api/admin/inscricoes", headers=headers)
    assert not any(i["id"] == inscricao_id for i in listagem.json())


def test_criar_inscricao_com_arquivo_nao_suportado_retorna_400(client):
    unidades = client.get("/api/unidades").json()
    anexos = client.get("/api/anexos").json()
    files = {"comprovante": ("comprovante.txt", io.BytesIO(b"nao e imagem nem pdf"), "text/plain")}
    data = {
        "nome_completo": "Servidor Invalido",
        "cpf": "529.982.247-25",
        "email": "arquivo@example.com",
        "unidade_id": str(unidades[0]["id"]),
        "anexo_id": str(anexos[0]["id"]),
    }
    resp = client.post("/api/inscricoes", data=data, files=files)
    assert resp.status_code == 400


def test_fluxo_completo_rejeicao_reenvio_aprovacao_checkin(client, db_session):
    resp = _submit_inscricao(client)
    assert resp.status_code == 201
    inscricao_id = resp.json()["id"]
    assert resp.json()["status"] == "pendente"

    admin_token = _admin_token(client)
    headers = {"Authorization": f"Bearer {admin_token}"}

    listagem = client.get("/api/admin/inscricoes", headers=headers)
    assert listagem.status_code == 200
    assert any(i["id"] == inscricao_id for i in listagem.json())

    rejeicao = client.post(
        f"/api/admin/inscricoes/{inscricao_id}/rejeitar",
        json={"motivo": "Valor do comprovante não confere."},
        headers=headers,
    )
    assert rejeicao.status_code == 200
    assert rejeicao.json()["status"] == "rejeitado"

    inscricao_db = db_session.query(models.Inscricao).filter_by(id=inscricao_id).first()
    reenvio_token = inscricao_db.reenvio_token

    reenvio_status = client.get(f"/api/inscricoes/reenvio/{reenvio_token}")
    assert reenvio_status.status_code == 200
    assert reenvio_status.json()["status"] == "rejeitado"

    files = {"comprovante": ("novo_comprovante.png", io.BytesIO(PNG_BYTES), "image/png")}
    reenvio = client.post(f"/api/inscricoes/reenvio/{reenvio_token}", files=files)
    assert reenvio.status_code == 200
    assert reenvio.json()["status"] == "pendente"

    aprovacao = client.post(f"/api/admin/inscricoes/{inscricao_id}/aprovar", headers=headers)
    assert aprovacao.status_code == 200
    assert aprovacao.json()["status"] == "aprovado"

    db_session.refresh(inscricao_db)
    qr_token = inscricao_db.qr_token
    assert qr_token

    checkin_token = _checkin_token(client)
    checkin_headers = {"Authorization": f"Bearer {checkin_token}"}

    primeiro_checkin = client.post(
        "/api/checkin/validar", json={"qr_token": qr_token}, headers=checkin_headers
    )
    assert primeiro_checkin.status_code == 200
    assert primeiro_checkin.json()["ok"] is True

    segundo_checkin = client.post(
        "/api/checkin/validar", json={"qr_token": qr_token}, headers=checkin_headers
    )
    assert segundo_checkin.status_code == 200
    assert segundo_checkin.json()["ok"] is False
    assert segundo_checkin.json()["ja_utilizado"] is True
