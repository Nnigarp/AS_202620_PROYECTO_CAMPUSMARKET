import os
import secrets
from datetime import datetime, timedelta, timezone

from backend.app.universidades.service import existe_activa

from .errors import AuthRateLimitError, InvalidCredentialsError
from .repository import (
    consume_auth_budget,
    create_session,
    create_user,
    find_user,
    revoke_session,
    session_user,
    update_profile,
)
from .security import DUMMY_PASSWORD_HASH, hash_password, token_digest, verify_password


def public_user(user: dict) -> dict:
    configured = os.getenv("CAMPUSMARKET_ADMIN_USER_IDS", "")
    admin_ids = {value.strip() for value in configured.split(",") if value.strip().isdigit()}
    return {
        "id": user["id"], "nombre": user["nombre"], "correo": user["correo"],
        "es_admin": str(user["id"]) in admin_ids,
        "universidad_id": user.get("universidad_id"),
    }


def _check_budget(action: str, correo: str, peer: str) -> None:
    # Peer procede de Request.client, nunca de un header aportado por el cliente.
    for scope, value, maximum in [("correo", correo, 10), ("peer", peer, 100)]:
        key = token_digest(f"{action}:{scope}:{value}")
        if not consume_auth_budget(key, maximum):
            raise AuthRateLimitError("Demasiados intentos. Intenta nuevamente en cinco minutos.")


def registrar(nombre: str, correo: str, password: str, peer: str, universidad_id: int | None = None) -> dict:
    correo = correo.strip().lower()
    _check_budget("registro", correo, peer)
    if universidad_id is not None and not existe_activa(universidad_id):
        raise ValueError("Selecciona una universidad válida de Cartagena.")
    return public_user(create_user(nombre.strip(), correo, hash_password(password), universidad_id))


def login(correo: str, password: str, peer: str) -> dict:
    correo = correo.strip().lower()
    _check_budget("login", correo, peer)
    user = find_user(correo)
    valid = verify_password(password, user["password_hash"] if user else DUMMY_PASSWORD_HASH)
    if not user or not valid:
        raise InvalidCredentialsError("Correo o contraseña incorrectos.")
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=12)
    create_session(token_digest(token), user["id"], expires.replace(tzinfo=None))
    return {"access_token": token, "token_type": "bearer", "expira_en": expires, "usuario": public_user(user)}


def autenticar(token: str) -> dict:
    if len(token) > 128:
        raise InvalidCredentialsError("Sesión inválida o expirada.")
    user = session_user(token_digest(token))
    if user is None:
        raise InvalidCredentialsError("Sesión inválida o expirada.")
    return public_user(user)


def logout(token: str) -> None:
    revoke_session(token_digest(token))


def editar_perfil(user_id: int, nombre: str, universidad_id: int | None = None) -> dict:
    if universidad_id is not None and not existe_activa(universidad_id):
        raise ValueError("Selecciona una universidad válida de Cartagena.")
    return public_user(update_profile(user_id, nombre.strip(), universidad_id))
