import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class StaffRole(str, enum.Enum):
    admin = "admin"
    checkin = "checkin"


class InscricaoStatus(str, enum.Enum):
    pendente = "pendente"
    aprovado = "aprovado"
    rejeitado = "rejeitado"


class Unidade(Base):
    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Anexo(Base):
    __tablename__ = "anexos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class StaffUser(Base):
    __tablename__ = "staff_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole), nullable=False)


class Inscricao(Base):
    __tablename__ = "inscricoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    anexo_id: Mapped[int] = mapped_column(ForeignKey("anexos.id"), nullable=False)
    unidade: Mapped["Unidade"] = relationship()
    anexo: Mapped["Anexo"] = relationship()

    comprovante_path: Mapped[str] = mapped_column(String(500), nullable=False)
    comprovante_mime: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[InscricaoStatus] = mapped_column(
        Enum(InscricaoStatus), default=InscricaoStatus.pendente, nullable=False
    )
    motivo_rejeicao: Mapped[str | None] = mapped_column(String(500), nullable=True)

    qr_token: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    reenvio_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
