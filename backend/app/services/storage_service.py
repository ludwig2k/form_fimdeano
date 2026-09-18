import os
import uuid

from fastapi import HTTPException, UploadFile, status

from ..config import settings

ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


async def save_comprovante(inscricao_id_hint: str, file: UploadFile) -> tuple[str, str]:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo não suportado. Envie uma imagem (JPG/PNG/WEBP) ou PDF.",
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo muito grande. O limite é de 5MB.",
        )
    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio.")

    folder = os.path.join(settings.upload_dir, inscricao_id_hint)
    os.makedirs(folder, exist_ok=True)

    ext = ALLOWED_MIME_TYPES[file.content_type]
    filename = f"{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(folder, filename)

    with open(full_path, "wb") as f:
        f.write(contents)

    return full_path, file.content_type


def delete_comprovante(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
