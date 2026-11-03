"""Favoritos es el único escritor de sus referencias privadas.

No modifica tablas de Usuarios/Publicaciones. El catálogo resuelve únicamente
referencias públicas vigentes; una referencia huérfana nunca publica contenido.
"""

from backend.app.db import transaction


def initialize_database() -> None:
    with transaction() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favoritos (
                usuario_id BIGINT UNSIGNED NOT NULL,
                publicacion_id BIGINT UNSIGNED NOT NULL,
                creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (usuario_id, publicacion_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)


def list_ids(usuario_id: int) -> list[int]:
    initialize_database()
    with transaction() as cursor:
        cursor.execute("""
            SELECT publicacion_id FROM favoritos
            WHERE usuario_id = %s ORDER BY creado_en DESC, publicacion_id DESC
        """, (usuario_id,))
        return [row["publicacion_id"] for row in cursor.fetchall()]


def add(usuario_id: int, publicacion_id: int) -> None:
    initialize_database()
    with transaction() as cursor:
        cursor.execute("""
            INSERT INTO favoritos (usuario_id, publicacion_id) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE publicacion_id = publicacion_id
        """, (usuario_id, publicacion_id))


def remove(usuario_id: int, publicacion_id: int) -> None:
    initialize_database()
    with transaction() as cursor:
        cursor.execute("""
            DELETE FROM favoritos WHERE usuario_id = %s AND publicacion_id = %s
        """, (usuario_id, publicacion_id))
