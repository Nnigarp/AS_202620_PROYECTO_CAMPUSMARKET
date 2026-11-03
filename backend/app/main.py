import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.app.administracion.router import router as administracion_router
from backend.app.catalogo.router import router as catalogo_router
from backend.app.db import PersistenceUnavailableError, database_is_available
from backend.app.observability import (
    get_ec01_metric,
    log_http_request,
)
from backend.app.publicaciones.router import router as publicaciones_router
from backend.app.resource_limits import RequestBodyLimitMiddleware
from backend.app.universidades.router import router as universidades_router
from backend.app.usuarios.router import router as usuarios_router


class HealthResponse(BaseModel):
    status: str
    service: str


app = FastAPI(
    title="CampusMarket API",
    version="2.0.0",
    responses={
        413: {
            "description": "La solicitud supera el límite permitido.",
            "content": {"application/json": {"schema": {
                "type": "object", "properties": {"detail": {"type": "string"}},
                "required": ["detail"],
            }}},
        },
    },
    description=(
        "API HTTP/JSON de CampusMarket para crear y consultar publicaciones. "
        "El contrato versionado es contracts/openapi-v2.json."
    ),
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Entorno local",
        }
    ],
)

app.add_middleware(RequestBodyLimitMiddleware)
app.middleware("http")(log_http_request)


@app.exception_handler(PersistenceUnavailableError)
async def persistence_error(request, error):
    return JSONResponse(status_code=503, content={"detail": "La persistencia está temporalmente no disponible. Intenta nuevamente."})


@app.exception_handler(RequestValidationError)
async def validation_error(request, error):
    # FastAPI normalmente incluye input: nunca reflejar una contraseña inválida.
    safe_errors = [{"loc": item["loc"], "msg": item["msg"], "type": item["type"]} for item in error.errors()]
    return JSONResponse(status_code=422, content={"detail": safe_errors})

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://nnigarp.github.io",
        "https://campusmarket.iscoutb.dev",
        *[origin.strip() for origin in os.getenv("CAMPUSMARKET_CORS_ORIGINS", "").split(",") if origin.strip()],
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_dir = Path(os.getenv("CAMPUSMARKET_UPLOAD_DIR", "backend/uploads"))
uploads_dir.mkdir(
    parents=True,
    exist_ok=True,
)

app.mount(
    "/uploads",
    StaticFiles(directory=uploads_dir),
    name="uploads",
)

app.include_router(publicaciones_router)
app.include_router(catalogo_router)
app.include_router(usuarios_router)
app.include_router(universidades_router)
app.include_router(administracion_router)


@app.get(
    "/ops/metrics/ec01",
    include_in_schema=False,
)
def ec01_metric():
    return get_ec01_metric()


@app.get(
    "/health",
    response_model=HealthResponse,
    operation_id="consultarSalud",
    summary="Consultar la salud del backend",
)
def health_check():
    if not database_is_available():
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "service": "campusmarket-api",
            },
        )

    return {
        "status": "ok",
        "service": "campusmarket-api",
    }
