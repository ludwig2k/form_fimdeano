import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..database import get_db
from ..security import create_access_token, require_admin, verify_password
from ..services import email_service, qrcode_service, storage_service

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[])


@router.post("/login", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.StaffUser).filter_by(
        username=form_data.username, role=models.StaffRole.admin
    ).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos.")
    token = create_access_token(user.username, user.role)
    return schemas.TokenResponse(access_token=token, role=user.role.value)


@router.get("/inscricoes", response_model=list[schemas.InscricaoAdminOut])
def listar_inscricoes(
    status_filtro: models.InscricaoStatus | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    query = db.query(models.Inscricao)
    if status_filtro:
        query = query.filter_by(status=status_filtro)
    return query.order_by(models.Inscricao.created_at.desc()).all()


@router.get("/inscricoes/{inscricao_id}/comprovante")
def obter_comprovante(inscricao_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    inscricao = db.get(models.Inscricao, inscricao_id)
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")
    return FileResponse(inscricao.comprovante_path, media_type=inscricao.comprovante_mime)


@router.delete("/inscricoes/{inscricao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_inscricao(inscricao_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    inscricao = db.get(models.Inscricao, inscricao_id)
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")

    storage_service.delete_comprovante(inscricao.comprovante_path)
    db.delete(inscricao)
    db.commit()


@router.post("/inscricoes/{inscricao_id}/aprovar", response_model=schemas.InscricaoAdminOut)
def aprovar_inscricao(inscricao_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    inscricao = db.get(models.Inscricao, inscricao_id)
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")
    if inscricao.status == models.InscricaoStatus.aprovado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inscrição já aprovada.")

    inscricao.status = models.InscricaoStatus.aprovado
    inscricao.motivo_rejeicao = None
    if not inscricao.qr_token:
        inscricao.qr_token = qrcode_service.generate_token()
    db.commit()
    db.refresh(inscricao)

    email_enviado = True
    try:
        qr_bytes = qrcode_service.generate_qr_png_bytes(inscricao.qr_token)
        email_service.send_aprovacao_email(inscricao.email, inscricao.nome_completo, inscricao.qr_token, qr_bytes)
    except Exception:
        email_enviado = False
        print(f"[admin] Falha ao enviar e-mail de aprovacao para {inscricao.email}:")
        print(traceback.format_exc())

    resultado = schemas.InscricaoAdminOut.model_validate(inscricao)
    resultado.email_enviado = email_enviado
    return resultado


@router.post("/inscricoes/{inscricao_id}/rejeitar", response_model=schemas.InscricaoAdminOut)
def rejeitar_inscricao(
    inscricao_id: int,
    payload: schemas.InscricaoRejeitar,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    inscricao = db.get(models.Inscricao, inscricao_id)
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")

    inscricao.status = models.InscricaoStatus.rejeitado
    inscricao.motivo_rejeicao = payload.motivo
    db.commit()
    db.refresh(inscricao)

    email_enviado = True
    try:
        reenvio_url = f"{settings.public_base_url}/reenvio/{inscricao.reenvio_token}"
        email_service.send_rejeicao_email(inscricao.email, inscricao.nome_completo, payload.motivo, reenvio_url)
    except Exception:
        email_enviado = False
        print(f"[admin] Falha ao enviar e-mail de rejeicao para {inscricao.email}:")
        print(traceback.format_exc())

    resultado = schemas.InscricaoAdminOut.model_validate(inscricao)
    resultado.email_enviado = email_enviado
    return resultado


@router.get("/unidades", response_model=list[schemas.UnidadeOut])
def listar_unidades_admin(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return db.query(models.Unidade).order_by(models.Unidade.nome).all()


@router.post("/unidades", response_model=schemas.UnidadeOut, status_code=status.HTTP_201_CREATED)
def criar_unidade(payload: schemas.UnidadeIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    unidade = models.Unidade(nome=payload.nome)
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade


@router.patch("/unidades/{unidade_id}/ativo", response_model=schemas.UnidadeOut)
def alternar_unidade(
    unidade_id: int, ativo: bool, db: Session = Depends(get_db), _: str = Depends(require_admin)
):
    unidade = db.get(models.Unidade, unidade_id)
    if not unidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")
    unidade.ativo = ativo
    db.commit()
    db.refresh(unidade)
    return unidade


@router.get("/anexos", response_model=list[schemas.AnexoOut])
def listar_anexos_admin(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return db.query(models.Anexo).order_by(models.Anexo.nome).all()


@router.post("/anexos", response_model=schemas.AnexoOut, status_code=status.HTTP_201_CREATED)
def criar_anexo(payload: schemas.AnexoIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    anexo = models.Anexo(nome=payload.nome)
    db.add(anexo)
    db.commit()
    db.refresh(anexo)
    return anexo


@router.patch("/anexos/{anexo_id}/ativo", response_model=schemas.AnexoOut)
def alternar_anexo(anexo_id: int, ativo: bool, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    anexo = db.get(models.Anexo, anexo_id)
    if not anexo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anexo não encontrado.")
    anexo.ativo = ativo
    db.commit()
    db.refresh(anexo)
    return anexo
