from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response

from backend.app.catalogo.schemas import PublicacionCatalogo
from backend.app.publicaciones.service import PublicationPersistenceUnavailableError
from backend.app.usuarios.dependencies import UsuarioActual

from .service import (
    FavoritePublicationUnavailableError,
    agregar_favorito,
    listar_favoritos,
    quitar_favorito,
)

router = APIRouter(prefix="/favoritos", tags=["favoritos"])
PublicacionId = Annotated[int, Path(gt=0, le=9223372036854775807)]


@router.get("", response_model=list[PublicacionCatalogo], operation_id="consultarMisFavoritos",
            summary="Consultar mis favoritos privados", responses={401: {}, 503: {}})
def consultar_favoritos(user: UsuarioActual, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        return listar_favoritos(user["id"])
    except PublicationPersistenceUnavailableError as error:
        raise HTTPException(503, "Los favoritos están temporalmente no disponibles.") from error


@router.put("/{publicacion_id}", status_code=204, operation_id="agregarMiFavorito",
            summary="Agregar a mis favoritos, sin duplicados", responses={401: {}, 404: {}, 503: {}})
def agregar(publicacion_id: PublicacionId, user: UsuarioActual):
    try:
        agregar_favorito(user["id"], publicacion_id)
    except FavoritePublicationUnavailableError as error:
        raise HTTPException(404, str(error)) from error
    except PublicationPersistenceUnavailableError as error:
        raise HTTPException(503, "Los favoritos están temporalmente no disponibles.") from error
    return Response(status_code=204, headers={"Cache-Control": "no-store"})


@router.delete("/{publicacion_id}", status_code=204, operation_id="quitarMiFavorito",
               summary="Quitar de mis favoritos", responses={401: {}, 503: {}})
def quitar(publicacion_id: PublicacionId, user: UsuarioActual):
    quitar_favorito(user["id"], publicacion_id)
    return Response(status_code=204, headers={"Cache-Control": "no-store"})
