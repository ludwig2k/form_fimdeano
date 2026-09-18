from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from .cpf import is_valid_cpf, mask_cpf, only_digits
from .models import InscricaoStatus


class UnidadeOut(BaseModel):
    id: int
    nome: str
    ativo: bool

    model_config = {"from_attributes": True}


class UnidadeIn(BaseModel):
    nome: str = Field(min_length=2, max_length=200)


class AnexoOut(BaseModel):
    id: int
    nome: str
    ativo: bool

    model_config = {"from_attributes": True}


class AnexoIn(BaseModel):
    nome: str = Field(min_length=2, max_length=200)


class InscricaoCreate(BaseModel):
    nome_completo: str = Field(min_length=3, max_length=200)
    cpf: str
    email: EmailStr
    unidade_id: int
    anexo_id: int

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        digits = only_digits(value)
        if not is_valid_cpf(digits):
            raise ValueError("CPF inválido")
        return digits


class InscricaoPublicOut(BaseModel):
    id: int
    status: InscricaoStatus

    model_config = {"from_attributes": True}


class InscricaoAdminOut(BaseModel):
    id: int
    nome_completo: str
    cpf: str
    email: str
    unidade: UnidadeOut
    anexo: AnexoOut
    status: InscricaoStatus
    motivo_rejeicao: str | None
    checked_in_at: datetime | None
    created_at: datetime
    comprovante_mime: str

    model_config = {"from_attributes": True}

    @field_validator("cpf")
    @classmethod
    def mask(cls, value: str) -> str:
        return mask_cpf(value)


class InscricaoRejeitar(BaseModel):
    motivo: str = Field(min_length=3, max_length=500)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class CheckinValidarRequest(BaseModel):
    qr_token: str


class CheckinValidarResponse(BaseModel):
    ok: bool
    mensagem: str
    nome_completo: str | None = None
    unidade: str | None = None
    anexo: str | None = None
    ja_utilizado: bool = False
    checked_in_at: datetime | None = None
