from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    File,
    Header,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.concurrency import run_in_threadpool

from backend.app.usuarios.dependencies import UsuarioActual

from .service import (
    PublicationIdempotencyConflictError,
    PublicationNotFoundError,
    PublicationPersistenceUnavailableError,
    cambiar_estado_publicacion,
    crear_publicacion,
    editar_publicacion,
    elegir_imagen_principal,
    eliminar_imagen_publicacion,
    eliminar_publicacion,
    listar_publicaciones,
    listar_publicaciones_propietario,
    subir_imagen_publicacion,
)

router = APIRouter(
    prefix="/publicaciones",
    tags=["publicaciones"],
)


class PublicacionBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    titulo: str = Field(min_length=3, max_length=100)
    descripcion: str = Field(min_length=3, max_length=500)
    precio: float = Field(gt=0, le=9999999999.99, allow_inf_nan=False)
    modalidad: Literal["venta", "alquiler"]
    estado: Literal["nuevo", "usado", "reacondicionado"]

    @field_validator("precio")
    @classmethod
    def precio_en_centavos(cls, value):
        if round(value, 2) != value:
            raise ValueError("El precio admite máximo dos decimales.")
        return value


class PublicacionCreate(PublicacionBase):
    estado_publicacion: Literal[
        "disponible",
        "reservado",
        "vendido",
    ] = "disponible"


class PublicacionUpdate(PublicacionBase):
    pass


class EstadoPublicacionUpdate(BaseModel):
    estado_publicacion: Literal[
        "disponible",
        "reservado",
        "vendido",
    ]


class Publicacion(PublicacionCreate):
    id: int
    propietario_id: int
    universidad_id: int | None = None
    visible: bool = True


class PublicacionImagen(BaseModel):
    id: int
    publicacion_id: int
    imagen_url: str
    orden: int
    es_principal: bool


class PublicacionGestion(Publicacion):
    imagenes: list[PublicacionImagen] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str


def _service_unavailable(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "La persistencia está temporalmente no disponible. "
            "Intenta nuevamente."
        ),
    )


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
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Idempotency-Key reutilizada con datos distintos o publicación ausente",
        },
    },
)
def crear(
    payload: PublicacionCreate,
    user: UsuarioActual,
    idempotency_key: str | None = Header(default=None, min_length=8, max_length=128, alias="Idempotency-Key"),
):
    try:
        return crear_publicacion(payload.model_dump(), user["id"], idempotency_key=idempotency_key)
    except PublicationIdempotencyConflictError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error


@router.get(
    "",
    response_model=list[Publicacion],
    operation_id="listarPublicaciones",
    summary="Listar publicaciones",
)
def listar():
    try:
        return listar_publicaciones()
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error


@router.get(
    "/mias",
    response_model=list[PublicacionGestion],
    operation_id="listarMisPublicaciones",
    summary="Listar publicaciones de un propietario",
)
def listar_mias(user: UsuarioActual):
    try:
        return listar_publicaciones_propietario(user["id"])
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error


@router.put(
    "/{publication_id}",
    response_model=Publicacion,
    operation_id="editarPublicacion",
    summary="Editar una publicación propia",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Publicación no encontrada para el propietario",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Persistencia temporalmente no disponible",
        },
    },
)
def editar(
    publication_id: int,
    payload: PublicacionUpdate,
    user: UsuarioActual,
):
    try:
        return editar_publicacion(
            publication_id,
            user["id"],
            payload.model_dump(),
        )
    except PublicationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error


@router.patch(
    "/{publication_id}/estado",
    response_model=Publicacion,
    operation_id="cambiarEstadoPublicacion",
    summary="Cambiar disponibilidad de una publicación propia",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Publicación no encontrada para el propietario",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Persistencia temporalmente no disponible",
        },
    },
)
def cambiar_estado(
    publication_id: int,
    payload: EstadoPublicacionUpdate,
    user: UsuarioActual,
):
    try:
        return cambiar_estado_publicacion(
            publication_id,
            user["id"],
            payload.estado_publicacion,
        )
    except PublicationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error


@router.delete(
    "/{publication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="eliminarPublicacion",
    summary="Eliminar una publicación propia",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Publicación no encontrada para el propietario",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Persistencia temporalmente no disponible",
        },
    },
)
def eliminar(publication_id: int, user: UsuarioActual):
    try:
        eliminar_publicacion(publication_id, user["id"])
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except PublicationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error


@router.post(
    "/{publication_id}/imagenes",
    response_model=PublicacionImagen,
    status_code=status.HTTP_201_CREATED,
    operation_id="subirImagenPublicacion",
    summary="Subir una imagen de una publicación",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Imagen inválida o máximo alcanzado",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Publicación no encontrada",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Persistencia temporalmente no disponible",
        },
    },
)
async def subir_imagen(
    publication_id: int,
    user: UsuarioActual,
    archivo: Annotated[UploadFile, File()],
):
    try:
        contenido = await archivo.read(5 * 1024 * 1024 + 1)
        return await run_in_threadpool(
            subir_imagen_publicacion, publication_id, user["id"], archivo.filename or "", contenido,
        )
    except PublicationNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    except ValueError as error:
        raise HTTPException(400, str(error)) from error
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error
    finally:
        await archivo.close()


@router.delete("/{publication_id}/imagenes/{image_id}", status_code=204, operation_id="eliminarImagenPublicacion")
def eliminar_imagen(publication_id: int, image_id: int, user: UsuarioActual):
    try:
        eliminar_imagen_publicacion(publication_id, user["id"], image_id)
        return Response(status_code=204)
    except PublicationNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error


@router.put("/{publication_id}/imagenes/{image_id}/principal", response_model=list[PublicacionImagen], operation_id="elegirImagenPrincipal")
def principal(publication_id: int, image_id: int, user: UsuarioActual):
    try:
        return elegir_imagen_principal(publication_id, user["id"], image_id)
    except PublicationNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    except PublicationPersistenceUnavailableError as error:
        raise _service_unavailable(error) from error
