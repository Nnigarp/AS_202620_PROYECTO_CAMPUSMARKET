from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StringConstraints

from backend.app.catalogo.schemas import PublicacionCatalogo
from backend.app.publicaciones.service import PublicationPersistenceUnavailableError
from backend.app.usuarios.dependencies import UsuarioActual

from .errors import (
    ConversationNotFoundError,
    ConversationUnavailableError,
    MessageIdempotencyConflictError,
)
from .service import (
    consultar_conversacion,
    consultar_mensajes,
    enviar_mensaje,
    iniciar_conversacion,
    listar_conversaciones,
)

router = APIRouter(prefix="/conversaciones", tags=["mensajeria"])
Identificador = Annotated[int, Path(gt=0, le=9223372036854775807)]
FechaUTC = Annotated[datetime, BeforeValidator(
    lambda value: value.replace(tzinfo=timezone.utc) if isinstance(value, datetime) and value.tzinfo is None else value,
)]


class ConversacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    publicacion_id: int = Field(gt=0, le=9223372036854775807)


class MensajeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    texto: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
    clave: str = Field(pattern="^[a-f0-9]{32}$")


class Mensaje(BaseModel):
    id: int
    conversacion_id: int
    remitente_id: int
    texto: str
    creado_en: FechaUTC


class Conversacion(BaseModel):
    id: int
    publicacion_id: int
    comprador_id: int
    vendedor_id: int
    creado_en: FechaUTC
    actualizado_en: FechaUTC
    publicacion: PublicacionCatalogo | None = None
    ultimo_mensaje: Mensaje | None = None


class PaginaMensajes(BaseModel):
    mensajes: list[Mensaje]
    hay_mas: bool


def _private(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"


def _call(function, *args):
    try:
        return function(*args)
    except ConversationNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    except (ConversationUnavailableError, MessageIdempotencyConflictError) as error:
        raise HTTPException(409, str(error)) from error
    except PublicationPersistenceUnavailableError as error:
        raise HTTPException(503, "La mensajería está temporalmente no disponible.") from error


@router.post("", response_model=Conversacion, operation_id="iniciarConversacion",
             summary="Contactar al vendedor o recuperar la conversación", responses={401: {}, 409: {}, 503: {}})
def iniciar(payload: ConversacionCreate, user: UsuarioActual, response: Response):
    _private(response)
    return _call(iniciar_conversacion, user["id"], payload.publicacion_id)


@router.get("", response_model=list[Conversacion], operation_id="consultarMiBandeja",
            summary="Consultar mis conversaciones", responses={401: {}, 503: {}})
def bandeja(user: UsuarioActual, response: Response,
            limite: int = Query(default=30, ge=1, le=50), desplazamiento: int = Query(default=0, ge=0, le=100000)):
    _private(response)
    return _call(listar_conversaciones, user["id"], limite, desplazamiento)


@router.get("/{conversacion_id}", response_model=Conversacion, operation_id="consultarConversacion",
            summary="Consultar una conversación propia", responses={401: {}, 404: {}, 503: {}})
def detalle(conversacion_id: Identificador, user: UsuarioActual, response: Response):
    _private(response)
    return _call(consultar_conversacion, user["id"], conversacion_id)


@router.get("/{conversacion_id}/mensajes", response_model=PaginaMensajes, operation_id="consultarMensajes",
            summary="Consultar mensajes propios en orden con cursor", responses={401: {}, 404: {}, 503: {}})
def mensajes(conversacion_id: Identificador, user: UsuarioActual, response: Response,
             despues_de: int = Query(default=0, ge=0, le=9223372036854775807),
             limite: int = Query(default=50, ge=1, le=100)):
    _private(response)
    return _call(consultar_mensajes, user["id"], conversacion_id, despues_de, limite)


@router.post("/{conversacion_id}/mensajes", response_model=Mensaje, status_code=201, operation_id="enviarMensaje",
             summary="Enviar como usuario autenticado, con clave de reintento", responses={401: {}, 404: {}, 409: {}, 503: {}})
def enviar(conversacion_id: Identificador, payload: MensajeCreate, user: UsuarioActual, response: Response):
    _private(response)
    return _call(enviar_mensaje, user["id"], conversacion_id, payload.texto, payload.clave)
