"""Persistencia del catálogo de instituciones declarado por los usuarios."""
from backend.app.db import transaction

from .catalogo import listar_instituciones


def initialize_database() -> None:
    with transaction() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS universidades (
                id BIGINT UNSIGNED NOT NULL PRIMARY KEY,
                nombre VARCHAR(160) NOT NULL UNIQUE,
                sigla VARCHAR(40) NOT NULL,
                ciudad VARCHAR(80) NOT NULL,
                activa BOOLEAN NOT NULL DEFAULT TRUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        # No sobrescribir nombres modificados administrativamente; alta idempotente.
        cursor.executemany("""
            INSERT IGNORE INTO universidades (id, nombre, sigla, ciudad, activa)
            VALUES (%s, %s, %s, %s, TRUE)
        """, [(u["id"], u["nombre"], u["sigla"], u["ciudad"]) for u in listar_instituciones()])


def listar_activas() -> list[dict]:
    initialize_database()
    with transaction() as cursor:
        cursor.execute("""
            SELECT id, nombre, sigla, ciudad
            FROM universidades
            WHERE activa = TRUE AND ciudad = 'Cartagena'
            ORDER BY nombre
        """)
        return cursor.fetchall()


def existe_activa(universidad_id: int) -> bool:
    initialize_database()
    with transaction() as cursor:
        cursor.execute(
            "SELECT 1 FROM universidades WHERE id = %s AND activa = TRUE LIMIT 1",
            (universidad_id,),
        )
        return cursor.fetchone() is not None


def listar_por_ids(ids: list[int]) -> list[dict]:
    """Institución declarada al publicar, incluso si posteriormente se inactiva."""
    unique_ids = tuple(dict.fromkeys(ids))
    if not unique_ids:
        return []
    initialize_database()
    with transaction() as cursor:
        placeholders = ", ".join(["%s"] * len(unique_ids))
        cursor.execute(
            f"SELECT id, nombre, sigla, ciudad FROM universidades WHERE id IN ({placeholders})",
            unique_ids,
        )
        return cursor.fetchall()
