from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings
from .models import StaffRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="/api/admin/login", auto_error=False)
oauth2_scheme_checkin = OAuth2PasswordBearer(tokenUrl="/api/checkin/login", auto_error=False)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(username: str, role: StaffRole) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": username, "role": role.value, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")


def require_role(required_role: StaffRole):
    scheme = oauth2_scheme_admin if required_role == StaffRole.admin else oauth2_scheme_checkin

    def dependency(token: str | None = Depends(scheme)) -> str:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
        payload = _decode_token(token)
        if payload.get("role") != required_role.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        return payload["sub"]

    return dependency


require_admin = require_role(StaffRole.admin)
require_checkin = require_role(StaffRole.checkin)
