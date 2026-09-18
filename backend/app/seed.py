from sqlalchemy.orm import Session

from .config import settings
from .models import Anexo, StaffRole, StaffUser, Unidade
from .security import hash_password

DEFAULT_UNIDADES = [
    "Gabinete",
    "Gerência de Gestão e Desenvolvimento de Pessoas",
    "Superintendência de Administração",
]

DEFAULT_ANEXOS = [
    "Anexo I",
    "Anexo II",
]


def seed_staff_users(db: Session) -> None:
    if not db.query(StaffUser).filter_by(role=StaffRole.admin).first():
        db.add(
            StaffUser(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                role=StaffRole.admin,
            )
        )
    if not db.query(StaffUser).filter_by(role=StaffRole.checkin).first():
        db.add(
            StaffUser(
                username=settings.checkin_username,
                password_hash=hash_password(settings.checkin_password),
                role=StaffRole.checkin,
            )
        )
    db.commit()


def seed_reference_data(db: Session) -> None:
    if db.query(Unidade).count() == 0:
        db.add_all(Unidade(nome=nome) for nome in DEFAULT_UNIDADES)
    if db.query(Anexo).count() == 0:
        db.add_all(Anexo(nome=nome) for nome in DEFAULT_ANEXOS)
    db.commit()


def run_seed(db: Session) -> None:
    seed_staff_users(db)
    seed_reference_data(db)
