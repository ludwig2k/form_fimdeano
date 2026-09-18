import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import admin, checkin, public
from .seed import run_seed

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    run_seed(db)

app = FastAPI(title="Confraternização SEAD 2026")

allowed_origins = {"http://localhost:37230", settings.public_base_url}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public.router)
app.include_router(admin.router)
app.include_router(checkin.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "static")

if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        candidate = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
