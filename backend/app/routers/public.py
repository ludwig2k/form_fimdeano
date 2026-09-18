from pydantic import ValidationError
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import qrcode_service, storage_service

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/unidades", response_model=list[schemas.UnidadeOut])
def listar_unidades(db: Session = Depends(get_db)):
    return db.query(models.Unidade).filter_by(ativo=True).order_by(models.Unidade.nome).all()


@router.get("/anexos", response_model=list[schemas.AnexoOut])
def listar_anexos(db: Session = Depends(get_db)):
    return db.query(models.Anexo).filter_by(ativo=True).order_by(models.Anexo.nome).all()


@router.post("/inscricoes", response_model=schemas.InscricaoPublicOut, status_code=status.HTTP_201_CREATED)
async def criar_inscricao(
    nome_completo: str = Form(...),
    cpf: str = Form(...),
    email: str = Form(...),
    unidade_id: int = Form(...),
    anexo_id: int = Form(...),
    comprovante: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        dados = schemas.InscricaoCreate(
            nome_completo=nome_completo, cpf=cpf, email=email, unidade_id=unidade_id, anexo_id=anexo_id
        )
    except ValidationError as exc:
        mensagens = [erro["msg"] for erro in exc.errors()]
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=mensagens)

    if not db.query(models.Unidade).filter_by(id=dados.unidade_id, ativo=True).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unidade de lotação inválida.")
    if not db.query(models.Anexo).filter_by(id=dados.anexo_id, ativo=True).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Anexo de lotação inválido.")

    if db.query(models.Inscricao).filter_by(cpf=dados.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma inscrição com este CPF. Verifique seu e-mail para mais informações.",
        )

    comprovante_path, comprovante_mime = await storage_service.save_comprovante("novo", comprovante)

    inscricao = models.Inscricao(
        nome_completo=dados.nome_completo,
        cpf=dados.cpf,
        email=dados.email,
        unidade_id=dados.unidade_id,
        anexo_id=dados.anexo_id,
        comprovante_path=comprovante_path,
        comprovante_mime=comprovante_mime,
        reenvio_token=qrcode_service.generate_token(),
    )
    db.add(inscricao)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        storage_service.delete_comprovante(comprovante_path)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma inscrição com este CPF. Verifique seu e-mail para mais informações.",
        )
    db.refresh(inscricao)
    return inscricao


@router.get("/inscricoes/reenvio/{reenvio_token}")
def obter_status_reenvio(reenvio_token: str, db: Session = Depends(get_db)):
    inscricao = db.query(models.Inscricao).filter_by(reenvio_token=reenvio_token).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link inválido.")
    return {
        "nome_completo": inscricao.nome_completo,
        "status": inscricao.status,
        "motivo_rejeicao": inscricao.motivo_rejeicao,
    }


@router.post("/inscricoes/reenvio/{reenvio_token}", response_model=schemas.InscricaoPublicOut)
async def reenviar_comprovante(
    reenvio_token: str,
    comprovante: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    inscricao = db.query(models.Inscricao).filter_by(reenvio_token=reenvio_token).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link inválido.")
    if inscricao.status != models.InscricaoStatus.rejeitado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta inscrição não está aguardando reenvio de comprovante.",
        )

    novo_path, novo_mime = await storage_service.save_comprovante(str(inscricao.id), comprovante)
    storage_service.delete_comprovante(inscricao.comprovante_path)

    inscricao.comprovante_path = novo_path
    inscricao.comprovante_mime = novo_mime
    inscricao.status = models.InscricaoStatus.pendente
    inscricao.motivo_rejeicao = None
    db.commit()
    db.refresh(inscricao)
    return inscricao
