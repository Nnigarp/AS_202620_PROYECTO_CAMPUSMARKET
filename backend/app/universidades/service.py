"""Capacidades de lectura públicas del contexto Universidades."""

from .repository import existe_activa as _existe_activa
from .repository import initialize_database, listar_activas, listar_por_ids


def asegurar_catalogo() -> None:
    """Inicializar antes de materializar la FK de Usuarios, sin importar su repositorio."""
    initialize_database()


def existe_activa(universidad_id: int) -> bool:
    return _existe_activa(universidad_id)


def listar_universidades() -> list[dict]:
    return listar_activas()


def obtener_universidades_por_ids(ids: list[int]) -> dict[int, dict]:
    return {row["id"]: row for row in listar_por_ids(ids)}
