"""Único escritor de conversaciones/mensajes; ninguna escritura en otros módulos."""

from backend.app.db import transaction

from .errors import ConversationNotFoundError, MessageIdempotencyConflictError


def initialize_database() -> None:
    with transaction() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversaciones (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                publicacion_id BIGINT UNSIGNED NOT NULL,
                comprador_id BIGINT UNSIGNED NOT NULL,
                vendedor_id BIGINT UNSIGNED NOT NULL,
                ultimo_mensaje_id BIGINT UNSIGNED NULL,
                creado_en DATETIME(6) NOT NULL,
                actualizado_en DATETIME(6) NOT NULL,
                UNIQUE (publicacion_id, comprador_id, vendedor_id),
                INDEX idx_conversacion_comprador (comprador_id, actualizado_en, id),
                INDEX idx_conversacion_vendedor (vendedor_id, actualizado_en, id),
                CHECK (comprador_id <> vendedor_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                conversacion_id BIGINT UNSIGNED NOT NULL,
                remitente_id BIGINT UNSIGNED NOT NULL,
                texto VARCHAR(2000) NOT NULL,
                clave CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
                creado_en DATETIME(6) NOT NULL,
                FOREIGN KEY (conversacion_id) REFERENCES conversaciones(id) ON DELETE CASCADE,
                UNIQUE (conversacion_id, remitente_id, clave),
                INDEX idx_mensajes_orden (conversacion_id, id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)


def _for_user(cursor, conversacion_id: int, usuario_id: int, *, lock: bool = False) -> dict:
    cursor.execute(
        "SELECT * FROM conversaciones WHERE id = %s AND (comprador_id = %s OR vendedor_id = %s)"
        + (" FOR UPDATE" if lock else ""),
        (conversacion_id, usuario_id, usuario_id),
    )
    data = cursor.fetchone()
    if data is None:
        # Igual respuesta para inexistente/ajena, sin revelar participantes.
        raise ConversationNotFoundError("Conversación no encontrada.")
    return data


def create_or_get(publicacion_id: int, comprador_id: int, vendedor_id: int) -> dict:
    initialize_database()
    with transaction() as cursor:
        cursor.execute("""
            INSERT INTO conversaciones (publicacion_id, comprador_id, vendedor_id, creado_en, actualizado_en)
            VALUES (%s, %s, %s, UTC_TIMESTAMP(6), UTC_TIMESTAMP(6))
            ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
        """, (publicacion_id, comprador_id, vendedor_id))
        return _for_user(cursor, cursor.lastrowid, comprador_id)


def find_for_user(conversacion_id: int, usuario_id: int) -> dict:
    initialize_database()
    with transaction() as cursor:
        return _for_user(cursor, conversacion_id, usuario_id)


def list_for_user(usuario_id: int, limite: int, desplazamiento: int) -> list[dict]:
    initialize_database()
    with transaction() as cursor:
        cursor.execute("""
            SELECT c.*, m.id AS mensaje_id, m.remitente_id AS mensaje_remitente,
                m.texto AS mensaje_texto, m.creado_en AS mensaje_fecha
            FROM conversaciones c LEFT JOIN mensajes m
                ON m.id = c.ultimo_mensaje_id AND m.conversacion_id = c.id
            WHERE c.comprador_id = %s OR c.vendedor_id = %s
            ORDER BY c.actualizado_en DESC, c.id DESC LIMIT %s OFFSET %s
        """, (usuario_id, usuario_id, limite, desplazamiento))
        result = []
        for row in cursor.fetchall():
            row["ultimo_mensaje"] = None if row["mensaje_id"] is None else {
                "id": row["mensaje_id"], "conversacion_id": row["id"],
                "remitente_id": row["mensaje_remitente"], "texto": row["mensaje_texto"],
                "creado_en": row["mensaje_fecha"],
            }
            result.append(row)
        return result


def list_messages(conversacion_id: int, usuario_id: int, despues_de: int, limite: int) -> list[dict]:
    initialize_database()
    with transaction() as cursor:
        _for_user(cursor, conversacion_id, usuario_id)
        cursor.execute("""
            SELECT id, conversacion_id, remitente_id, texto, creado_en FROM mensajes
            WHERE conversacion_id = %s AND id > %s ORDER BY id LIMIT %s
        """, (conversacion_id, despues_de, limite))
        return cursor.fetchall()


def create_message(conversacion_id: int, usuario_id: int, texto: str, clave: str) -> dict:
    initialize_database()
    with transaction() as cursor:
        _for_user(cursor, conversacion_id, usuario_id, lock=True)
        cursor.execute("""
            SELECT id, conversacion_id, remitente_id, texto, creado_en FROM mensajes
            WHERE conversacion_id = %s AND remitente_id = %s AND clave = %s
        """, (conversacion_id, usuario_id, clave))
        existing = cursor.fetchone()
        if existing:
            if existing["texto"] != texto:
                raise MessageIdempotencyConflictError("La clave ya corresponde a otro mensaje.")
            return existing
        cursor.execute("""
            INSERT INTO mensajes (conversacion_id, remitente_id, texto, clave, creado_en)
            VALUES (%s, %s, %s, %s, UTC_TIMESTAMP(6))
        """, (conversacion_id, usuario_id, texto, clave))
        id_ = cursor.lastrowid
        cursor.execute("""
            UPDATE conversaciones SET ultimo_mensaje_id = %s, actualizado_en = UTC_TIMESTAMP(6)
            WHERE id = %s
        """, (id_, conversacion_id))
        cursor.execute("SELECT id, conversacion_id, remitente_id, texto, creado_en FROM mensajes WHERE id = %s", (id_,))
        return cursor.fetchone()
