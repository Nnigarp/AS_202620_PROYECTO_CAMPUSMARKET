from .image_storage import delete_publication_image, save_publication_image
from .repository import (
    IdempotencyConflictError,
    PersistenceUnavailableError,
    create_publication,
    create_publication_image,
    delete_publication,
    get_publication,
    hide_publication,
    list_publication_images,
    list_publication_images_batch,
    list_publications,
    list_publications_by_ids,
    list_publications_by_owner,
    publication_exists,
    remove_publication_image,
    set_primary_image,
    update_publication,
    update_publication_status,
)


class PublicationPersistenceUnavailableError(RuntimeError):
    """No es posible guardar o consultar publicaciones temporalmente."""


class PublicationIdempotencyConflictError(ValueError):
    """Clave de idempotencia reutilizada de forma incompatible."""


class PublicationNotFoundError(LookupError):
    """La publicación no existe o no pertenece al propietario indicado."""


def _normalizar_publicacion(data: dict) -> dict:
    return {
        "titulo": data["titulo"].strip(),
        "descripcion": data["descripcion"].strip(),
        "precio": float(data["precio"]),
        "modalidad": data["modalidad"],
        "estado": data["estado"],
    }


def crear_publicacion(data: dict, propietario_id: int, idempotency_key: str | None = None) -> dict:
    normalized = {
        **_normalizar_publicacion(data),
        "propietario_id": propietario_id,
        "estado_publicacion": data.get(
            "estado_publicacion",
            "disponible",
        ),
    }

    try:
        return create_publication(normalized, idempotency_key=idempotency_key)
    except IdempotencyConflictError as error:
        raise PublicationIdempotencyConflictError(str(error)) from error
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible guardar la publicación temporalmente."
        ) from error


def listar_publicaciones() -> list[dict]:
    try:
        return list_publications()
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible consultar las publicaciones temporalmente."
        ) from error


def listar_publicaciones_por_ids(publicacion_ids: list[int]) -> list[dict]:
    try:
        return list_publications_by_ids(publicacion_ids)
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError("No es posible consultar publicaciones temporalmente.") from error


def listar_publicaciones_propietario(
    propietario_id: int,
) -> list[dict]:
    try:
        publicaciones = list_publications_by_owner(propietario_id)
        return [
            {
                **publicacion,
                "imagenes": list_publication_images(publicacion["id"]),
            }
            for publicacion in publicaciones
        ]
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible consultar las publicaciones temporalmente."
        ) from error


def obtener_publicacion(publicacion_id: int) -> dict | None:
    try:
        return get_publication(publicacion_id)
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible consultar la publicación temporalmente."
        ) from error


def editar_publicacion(
    publicacion_id: int,
    propietario_id: int,
    data: dict,
) -> dict:
    try:
        updated = update_publication(
            publicacion_id,
            propietario_id,
            _normalizar_publicacion(data),
        )
        if updated is None:
            raise PublicationNotFoundError(
                "La publicación no existe o no pertenece al propietario."
            )
        return updated
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible editar la publicación temporalmente."
        ) from error


def cambiar_estado_publicacion(
    publicacion_id: int,
    propietario_id: int,
    estado_publicacion: str,
) -> dict:
    try:
        updated = update_publication_status(
            publicacion_id,
            propietario_id,
            estado_publicacion,
        )
        if updated is None:
            raise PublicationNotFoundError(
                "La publicación no existe o no pertenece al propietario."
            )
        return updated
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible cambiar el estado temporalmente."
        ) from error


def eliminar_publicacion(
    publicacion_id: int,
    propietario_id: int,
) -> None:
    try:
        imagenes = list_publication_images(publicacion_id)
        deleted = delete_publication(publicacion_id, propietario_id)
        if not deleted:
            raise PublicationNotFoundError(
                "La publicación no existe o no pertenece al propietario."
            )

        for imagen in imagenes:
            delete_publication_image(imagen["imagen_url"])
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible eliminar la publicación temporalmente."
        ) from error


def listar_imagenes_publicacion(
    publicacion_id: int,
) -> list[dict]:
    try:
        return list_publication_images(publicacion_id)
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible consultar las imágenes "
            "de la publicación temporalmente."
        ) from error


def existe_publicacion(publicacion_id: int) -> bool:
    try:
        return publication_exists(publicacion_id)
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible consultar la publicación temporalmente."
        ) from error


def registrar_imagen_publicacion(
    publicacion_id: int,
    propietario_id: int,
    imagen_url: str,
) -> dict:
    try:
        return create_publication_image(publicacion_id, propietario_id, imagen_url)
    except LookupError as error:
        raise PublicationNotFoundError(str(error)) from error
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible registrar la imagen temporalmente."
        ) from error


def verificar_propietario(publicacion_id: int, propietario_id: int) -> None:
    publicacion = obtener_publicacion(publicacion_id)
    if publicacion is None or publicacion["propietario_id"] != propietario_id:
        raise PublicationNotFoundError("La publicación no existe o no te pertenece.")


def subir_imagen_publicacion(publicacion_id: int, propietario_id: int, nombre: str, contenido: bytes) -> dict:
    verificar_propietario(publicacion_id, propietario_id)
    imagen_url = save_publication_image(publicacion_id, nombre, contenido)
    try:
        return registrar_imagen_publicacion(publicacion_id, propietario_id, imagen_url)
    except Exception:
        delete_publication_image(imagen_url)
        raise


def eliminar_imagen_publicacion(publicacion_id: int, propietario_id: int, imagen_id: int) -> None:
    try:
        url = remove_publication_image(publicacion_id, propietario_id, imagen_id)
        if url is None:
            raise PublicationNotFoundError("La imagen no existe o no te pertenece.")
        delete_publication_image(url)
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError("Persistencia temporalmente no disponible.") from error


def elegir_imagen_principal(publicacion_id: int, propietario_id: int, imagen_id: int) -> list[dict]:
    try:
        if not set_primary_image(publicacion_id, propietario_id, imagen_id):
            raise PublicationNotFoundError("La imagen no existe o no te pertenece.")
        return list_publication_images(publicacion_id)
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError("Persistencia temporalmente no disponible.") from error


def ocultar_publicacion(publicacion_id: int) -> bool:
    """Interfaz interna para administración; no cambia propiedad ni borra datos."""
    try:
        return hide_publication(publicacion_id)
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError("Persistencia temporalmente no disponible.") from error


def listar_imagenes_publicaciones(publicacion_ids: list[int]) -> dict[int, list[dict]]:
    """Interfaz interna de lectura en lote para Catálogo, sin acceso a repository."""
    try:
        return list_publication_images_batch(publicacion_ids)
    except PersistenceUnavailableError as error:
        raise PublicationPersistenceUnavailableError(
            "No es posible consultar las imágenes temporalmente."
        ) from error
