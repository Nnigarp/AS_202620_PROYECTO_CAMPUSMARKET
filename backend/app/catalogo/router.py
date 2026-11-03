from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.publicaciones.service import (
    PublicationPersistenceUnavailableError,
)

from .schemas import PublicacionCatalogo
from .service import buscar_publicaciones, obtener_publicacion

router = APIRouter(prefix="/catalogo", tags=["catalogo"])


@router.get(
    "",
    response_model=list[PublicacionCatalogo],
    operation_id="consultarCatalogo",
    summary="Consultar el catálogo",
)
def consultar_catalogo(
    q: str | None = Query(default=None, max_length=100),
    modalidad: Literal["venta", "alquiler"] | None = None,
    estado: Literal["nuevo", "usado", "reacondicionado"] | None = None,
    precio_min: float | None = Query(default=None, ge=0, allow_inf_nan=False),
    precio_max: float | None = Query(default=None, ge=0, allow_inf_nan=False),
    universidad_id: int | None = Query(default=None, ge=1),
):
    if (
        precio_min is not None
        and precio_max is not None
        and precio_min > precio_max
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="precio_min no puede ser mayor que precio_max",
        )

    try:
        return buscar_publicaciones(
            texto=q,
            modalidad=modalidad,
            estado=estado,
            precio_min=precio_min,
            precio_max=precio_max,
            universidad_id=universidad_id,
        )
    except PublicationPersistenceUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El catálogo está temporalmente no disponible.",
        ) from error


@router.get(
    "/{publicacion_id}",
    response_model=PublicacionCatalogo,
    operation_id="consultarDetallePublicacion",
    summary="Consultar el detalle de una publicación",
)
def consultar_detalle(publicacion_id: int):
    try:
        publicacion = obtener_publicacion(publicacion_id)
    except PublicationPersistenceUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El catálogo está temporalmente no disponible.",
        ) from error

    if publicacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicación no encontrada",
        )

    return publicacion
