from backend.app.catalogo.service import obtener_publicaciones_por_ids

from .repository import add, list_ids, remove


class FavoritePublicationUnavailableError(LookupError):
    """La referencia no apunta a una publicación pública vigente."""


def listar_favoritos(usuario_id: int) -> list[dict]:
    return obtener_publicaciones_por_ids(list_ids(usuario_id))


def agregar_favorito(usuario_id: int, publicacion_id: int) -> None:
    if not obtener_publicaciones_por_ids([publicacion_id]):
        raise FavoritePublicationUnavailableError("Esta publicación ya no está disponible.")
    add(usuario_id, publicacion_id)


def quitar_favorito(usuario_id: int, publicacion_id: int) -> None:
    # Idempotente, incluso si el propietario eliminó u ocultó la publicación.
    remove(usuario_id, publicacion_id)
