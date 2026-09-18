from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import create_access_token, require_checkin, verify_password

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.StaffUser).filter_by(
        username=form_data.username, role=models.StaffRole.checkin
    ).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos.")
    token = create_access_token(user.username, user.role)
    return schemas.TokenResponse(access_token=token, role=user.role.value)


@router.post("/validar", response_model=schemas.CheckinValidarResponse)
def validar_checkin(
    payload: schemas.CheckinValidarRequest,
    db: Session = Depends(get_db),
    _: str = Depends(require_checkin),
):
    inscricao = db.query(models.Inscricao).filter_by(qr_token=payload.qr_token).first()
    if not inscricao or inscricao.status != models.InscricaoStatus.aprovado:
        return schemas.CheckinValidarResponse(ok=False, mensagem="QR Code inválido ou inscrição não aprovada.")

    if inscricao.checked_in_at is not None:
        return schemas.CheckinValidarResponse(
            ok=False,
            mensagem="Este QR Code já foi utilizado.",
            nome_completo=inscricao.nome_completo,
            unidade=inscricao.unidade.nome,
            anexo=inscricao.anexo.nome,
            ja_utilizado=True,
            checked_in_at=inscricao.checked_in_at,
        )

    inscricao.checked_in_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(inscricao)

    return schemas.CheckinValidarResponse(
        ok=True,
        mensagem="Check-in realizado com sucesso!",
        nome_completo=inscricao.nome_completo,
        unidade=inscricao.unidade.nome,
        anexo=inscricao.anexo.nome,
        checked_in_at=inscricao.checked_in_at,
    )
