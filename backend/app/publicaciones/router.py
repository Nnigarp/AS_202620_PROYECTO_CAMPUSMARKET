from typing import Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from .service import (
    PublicationPersistenceUnavailableError,
    crear_publicacion,
    listar_publicaciones,
)

router = APIRouter(prefix="/publicaciones", tags=["publicaciones"])


class PublicacionCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    descripcion: str = Field(min_length=3, max_length=500)
    precio: float = Field(gt=0)
    modalidad: Literal["venta", "alquiler"]
    estado: Literal["nuevo", "usado", "reacondicionado"]


class Publicacion(PublicacionCreate):
    id: int


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "",
    response_model=Publicacion,
    status_code=status.HTTP_201_CREATED,
    operation_id="crearPublicacion",
    summary="Crear una publicación",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Persistencia temporalmente no disponible",
        }
    },
)
def crear(payload: PublicacionCreate):
    try:
        return crear_publicacion(payload.model_dump())
    except PublicationPersistenceUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La persistencia está temporalmente no disponible. Intenta nuevamente.",
        ) from error


@router.get(
    "",
    response_model=list[Publicacion],
    operation_id="listarPublicaciones",
    summary="Listar publicaciones",
)
def listar():
    return listar_publicaciones()
