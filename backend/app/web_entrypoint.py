"""Empaquetado Web de la imagen previa; el contrato API permanece en main.app."""

from pathlib import Path

from fastapi.staticfiles import StaticFiles

from backend.app.main import app

web_directory = Path("/app/frontend_web")
if not (web_directory / "index.html").is_file():
    raise RuntimeError("Flutter Web release artifacts missing")

app.mount("/app", StaticFiles(directory=web_directory, html=True), name="flutter-web")
