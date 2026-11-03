from backend.app.catalogo.service import obtener_publicaciones_por_ids

from .errors import ConversationUnavailableError
from .repository import (
    create_message,
    create_or_get,
    find_for_user,
    list_for_user,
    list_messages,
)


def _publicacion(id_: int) -> dict | None:
    values = obtener_publicaciones_por_ids([id_])
    return values[0] if values else None


def iniciar_conversacion(usuario_id: int, publicacion_id: int) -> dict:
    publicacion = _publicacion(publicacion_id)
    if not publicacion:
        raise ConversationUnavailableError("Esta publicación ya no está disponible.")
    vendedor_id = publicacion["propietario_id"]
    if vendedor_id == usuario_id:
        raise ConversationUnavailableError("No puedes iniciar una conversación contigo mismo.")
    return {**create_or_get(publicacion_id, usuario_id, vendedor_id), "publicacion": publicacion}


def consultar_conversacion(usuario_id: int, conversacion_id: int) -> dict:
    data = find_for_user(conversacion_id, usuario_id)
    return {**data, "publicacion": _publicacion(data["publicacion_id"])}


def listar_conversaciones(usuario_id: int, limite: int, desplazamiento: int) -> list[dict]:
    values = list_for_user(usuario_id, limite, desplazamiento)
    ids = list(dict.fromkeys(v["publicacion_id"] for v in values))
    publications = {p["id"]: p for p in obtener_publicaciones_por_ids(ids)}
    return [{**v, "publicacion": publications.get(v["publicacion_id"])} for v in values]


def consultar_mensajes(usuario_id: int, conversacion_id: int, despues_de: int, limite: int) -> dict:
    values = list_messages(conversacion_id, usuario_id, despues_de, limite + 1)
    return {"mensajes": values[:limite], "hay_mas": len(values) > limite}


def enviar_mensaje(usuario_id: int, conversacion_id: int, texto: str, clave: str) -> dict:
    data = find_for_user(conversacion_id, usuario_id)
    publication = _publicacion(data["publicacion_id"])
    if not publication or publication["propietario_id"] != data["vendedor_id"]:
        raise ConversationUnavailableError("La publicación ya no está disponible para nuevos mensajes.")
    return create_message(conversacion_id, usuario_id, texto, clave)
