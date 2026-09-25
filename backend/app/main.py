from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.app.observability import (
    get_ec01_metric,
    log_http_request,
)
from backend.app.publicaciones.repository import database_is_available
from backend.app.publicaciones.router import router as publicaciones_router


class HealthResponse(BaseModel):
    status: str
    service: str


app = FastAPI(
    title="CampusMarket API",
    version="1.0.0",
    description=(
        "API HTTP/JSON de CampusMarket para crear y consultar publicaciones. "
        "El contrato versionado es contracts/openapi-v1.json."
    ),
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Entorno local",
        }
    ],
)

app.middleware("http")(log_http_request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(publicaciones_router)


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
