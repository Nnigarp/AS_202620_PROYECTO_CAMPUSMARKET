import hashlib
import json

import pymysql

from backend.app.db import PersistenceUnavailableError, transaction
from backend.app.db import connect as _connect


class IdempotencyConflictError(ValueError):
    """La clave ya se usó para otra solicitud o el recurso ya no existe."""


def _payload_hash(data: dict) -> str:
    # Los datos ya fueron normalizados por el servicio.
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        LIMIT 1
        """,
        (table_name, column_name),
    )
    return cursor.fetchone() is not None


def initialize_database() -> None:
    connection = None

    try:
        connection = _connect()

        with connection.cursor() as cursor:
            cursor.execute("SELECT GET_LOCK(CONCAT('cm:pub:', LEFT(SHA2(DATABASE(), 256), 40)), 5) AS acquired")
            if cursor.fetchone()["acquired"] != 1:
                raise PersistenceUnavailableError("La inicialización de Publicaciones está temporalmente ocupada.")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS publicaciones (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                    titulo VARCHAR(100) NOT NULL,
                    descripcion VARCHAR(500) NOT NULL,
                    precio DECIMAL(12, 2) NOT NULL,
                    modalidad ENUM('venta', 'alquiler') NOT NULL,
                    estado ENUM(
                        'nuevo',
                        'usado',
                        'reacondicionado'
                    ) NOT NULL,
                    propietario_id BIGINT UNSIGNED NULL,
                    visible BOOLEAN NOT NULL DEFAULT TRUE,
                    estado_publicacion ENUM(
                        'disponible',
                        'reservado',
                        'vendido'
                    ) NOT NULL DEFAULT 'disponible',
                    PRIMARY KEY (id),
                    CONSTRAINT chk_publicaciones_precio
                        CHECK (precio > 0)
                )
                """
            )

            if not _column_exists(cursor, "publicaciones", "propietario_id"):
                cursor.execute("ALTER TABLE publicaciones ADD COLUMN propietario_id BIGINT UNSIGNED NULL")
            cursor.execute("""
                SELECT COLUMN_DEFAULT FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'publicaciones'
                  AND COLUMN_NAME = 'propietario_id'
            """)
            # Solo el esquema heredado tenía DEFAULT 1. Nunca conceder esas filas
            # a la primera cuenta registrada. MySQL DDL tiene commit implícito:
            # vaciar identidad bajo el esquema anterior ANTES de retirar el default.
            if str(cursor.fetchone()["COLUMN_DEFAULT"]) == "1":
                cursor.execute("ALTER TABLE publicaciones MODIFY propietario_id BIGINT UNSIGNED NULL DEFAULT 1")
                cursor.execute("UPDATE publicaciones SET propietario_id = NULL")
                connection.commit()
                cursor.execute("ALTER TABLE publicaciones MODIFY propietario_id BIGINT UNSIGNED NULL")
            if not _column_exists(cursor, "publicaciones", "universidad_id"):
                # NULL conserva publicaciones anteriores sin inferir universidad.
                cursor.execute("ALTER TABLE publicaciones ADD COLUMN universidad_id BIGINT UNSIGNED NULL")
            if not _column_exists(cursor, "publicaciones", "visible"):
                cursor.execute("ALTER TABLE publicaciones ADD COLUMN visible BOOLEAN NOT NULL DEFAULT TRUE")

            if not _column_exists(
                cursor,
                "publicaciones",
                "estado_publicacion",
            ):
                cursor.execute(
                    """
                    ALTER TABLE publicaciones
                    ADD COLUMN estado_publicacion ENUM(
                        'disponible',
                        'reservado',
                        'vendido'
                    ) NOT NULL DEFAULT 'disponible'
                    """
                )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS publicacion_imagenes (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                    publicacion_id BIGINT UNSIGNED NOT NULL,
                    imagen_url VARCHAR(500) NOT NULL,
                    orden TINYINT UNSIGNED NOT NULL,
                    es_principal BOOLEAN NOT NULL DEFAULT FALSE,
                    PRIMARY KEY (id),
                    CONSTRAINT fk_publicacion_imagenes_publicacion
                        FOREIGN KEY (publicacion_id)
                        REFERENCES publicaciones(id)
                        ON DELETE CASCADE,
                    CONSTRAINT uq_publicacion_imagenes_orden
                        UNIQUE (publicacion_id, orden),
                    CONSTRAINT chk_publicacion_imagenes_orden
                        CHECK (orden BETWEEN 1 AND 3)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS solicitudes_idempotentes (
                    propietario_id BIGINT UNSIGNED NOT NULL,
                    operacion VARCHAR(64) NOT NULL,
                    clave VARCHAR(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
                    payload_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
                    publicacion_id BIGINT UNSIGNED NULL,
                    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (propietario_id, operacion, clave)
                ) ENGINE=InnoDB
                """
            )

        connection.commit()

    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()

        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error

    finally:
        if connection:
            connection.close()


def _select_publication_fields() -> str:
    return """
        id,
        titulo,
        descripcion,
        CAST(precio AS DOUBLE) AS precio,
        modalidad,
        estado,
        propietario_id,
        universidad_id,
        estado_publicacion,
        visible
    """


def create_publication(data: dict, idempotency_key: str | None = None) -> dict:
    initialize_database()
    connection = None

    try:
        connection = _connect()

        with connection.cursor() as cursor:
            if idempotency_key is not None:
                payload_hash = _payload_hash(data)
                try:
                    cursor.execute(
                        """
                        INSERT INTO solicitudes_idempotentes
                            (propietario_id, operacion, clave, payload_hash)
                        VALUES (%s, 'crear_publicacion', %s, %s)
                        """,
                        (data["propietario_id"], idempotency_key, payload_hash),
                    )
                except pymysql.err.IntegrityError as error:
                    if error.args[0] != 1062:
                        raise
                    # La UNIQUE de InnoDB espera a que el primer intento
                    # haga COMMIT/ROLLBACK antes de informar duplicado.
                    connection.rollback()
                    cursor.execute(
                        """
                        SELECT payload_hash, publicacion_id
                        FROM solicitudes_idempotentes
                        WHERE propietario_id = %s AND operacion = 'crear_publicacion' AND clave = %s
                        """,
                        (data["propietario_id"], idempotency_key),
                    )
                    previous = cursor.fetchone()
                    if previous is None or previous["payload_hash"] != payload_hash or previous["publicacion_id"] is None:
                        raise IdempotencyConflictError("Idempotency-Key ya utilizada con otra solicitud.")
                    cursor.execute(
                        f"""
                        SELECT {_select_publication_fields()} FROM publicaciones
                        WHERE id = %s AND propietario_id = %s
                        """,
                        (previous["publicacion_id"], data["propietario_id"]),
                    )
                    existing = cursor.fetchone()
                    if existing is None:
                        raise IdempotencyConflictError("La publicación original ya no está disponible.")
                    return existing

            # Universidad declarada por el autor al crear; no se acepta desde el cliente.
            cursor.execute("SELECT universidad_id FROM usuarios WHERE id = %s", (data["propietario_id"],))
            autor = cursor.fetchone()
            universidad_id = autor["universidad_id"] if autor else None
            cursor.execute(
                """
                INSERT INTO publicaciones (
                    titulo,
                    descripcion,
                    precio,
                    modalidad,
                    estado,
                    propietario_id,
                    universidad_id,
                    estado_publicacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["titulo"],
                    data["descripcion"],
                    data["precio"],
                    data["modalidad"],
                    data["estado"],
                    data["propietario_id"],
                    universidad_id,
                    data["estado_publicacion"],
                ),
            )

            publication_id = cursor.lastrowid
            cursor.execute(
                f"""
                SELECT {_select_publication_fields()}
                FROM publicaciones
                WHERE id = %s AND propietario_id = %s
                """,
                (publication_id, data["propietario_id"]),
            )
            row = cursor.fetchone()
            if idempotency_key is not None:
                cursor.execute(
                    """
                    UPDATE solicitudes_idempotentes SET publicacion_id = %s
                    WHERE propietario_id = %s AND operacion = 'crear_publicacion' AND clave = %s
                    """,
                    (publication_id, data["propietario_id"], idempotency_key),
                )

        connection.commit()
        return row

    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def list_publications() -> list[dict]:
    initialize_database()
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_select_publication_fields()}
                FROM publicaciones
                WHERE visible = TRUE AND propietario_id IS NOT NULL
                ORDER BY id DESC
                """
            )
            return cursor.fetchall()
    except pymysql.MySQLError as error:
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def list_publications_by_owner(propietario_id: int) -> list[dict]:
    initialize_database()
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_select_publication_fields()}
                FROM publicaciones
                WHERE propietario_id = %s
                ORDER BY id DESC
                """,
                (propietario_id,),
            )
            return cursor.fetchall()
    except pymysql.MySQLError as error:
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def get_publication(publication_id: int) -> dict | None:
    initialize_database()
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_select_publication_fields()}
                FROM publicaciones
                WHERE id = %s
                """,
                (publication_id,),
            )
            return cursor.fetchone()
    except pymysql.MySQLError as error:
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def publication_exists(publication_id: int) -> bool:
    return get_publication(publication_id) is not None


def update_publication(
    publication_id: int,
    propietario_id: int,
    data: dict,
) -> dict | None:
    initialize_database()
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE publicaciones
                SET titulo = %s,
                    descripcion = %s,
                    precio = %s,
                    modalidad = %s,
                    estado = %s
                WHERE id = %s
                  AND propietario_id = %s
                """,
                (
                    data["titulo"],
                    data["descripcion"],
                    data["precio"],
                    data["modalidad"],
                    data["estado"],
                    publication_id,
                    propietario_id,
                ),
            )

            cursor.execute(
                f"""
                SELECT {_select_publication_fields()}
                FROM publicaciones
                WHERE id = %s AND propietario_id = %s
                """,
                (publication_id, propietario_id),
            )
            row = cursor.fetchone()

        connection.commit()
        return row
    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def update_publication_status(
    publication_id: int,
    propietario_id: int,
    estado_publicacion: str,
) -> dict | None:
    initialize_database()
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE publicaciones
                SET estado_publicacion = %s
                WHERE id = %s
                  AND propietario_id = %s
                """,
                (
                    estado_publicacion,
                    publication_id,
                    propietario_id,
                ),
            )

            cursor.execute(
                f"""
                SELECT {_select_publication_fields()}
                FROM publicaciones
                WHERE id = %s AND propietario_id = %s
                """,
                (publication_id, propietario_id),
            )
            row = cursor.fetchone()

        connection.commit()
        return row
    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def delete_publication(publication_id: int, propietario_id: int) -> bool:
    initialize_database()
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM publicaciones
                WHERE id = %s
                  AND propietario_id = %s
                """,
                (publication_id, propietario_id),
            )
            deleted = cursor.rowcount > 0

        connection.commit()
        return deleted
    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def list_publication_images(publication_id: int) -> list[dict]:
    initialize_database()
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    publicacion_id,
                    imagen_url,
                    orden,
                    es_principal
                FROM publicacion_imagenes
                WHERE publicacion_id = %s
                ORDER BY orden ASC
                """,
                (publication_id,),
            )
            return cursor.fetchall()
    except pymysql.MySQLError as error:
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def count_publication_images(publication_id: int) -> int:
    return len(list_publication_images(publication_id))


def create_publication_image(
    publication_id: int,
    propietario_id: int,
    imagen_url: str,
) -> dict:
    initialize_database()
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM publicaciones WHERE id = %s AND propietario_id = %s FOR UPDATE", (publication_id, propietario_id))
            if cursor.fetchone() is None:
                raise LookupError("La publicación no existe o no te pertenece.")
            cursor.execute("SELECT orden, es_principal FROM publicacion_imagenes WHERE publicacion_id = %s", (publication_id,))
            images = cursor.fetchall()
            if len(images) >= 3:
                raise ValueError("La publicación ya tiene el máximo de 3 imágenes.")
            used = {int(image["orden"]) for image in images}
            orden = next(value for value in range(1, 4) if value not in used)
            es_principal = not images
            cursor.execute(
                """
                INSERT INTO publicacion_imagenes (
                    publicacion_id,
                    imagen_url,
                    orden,
                    es_principal
                )
                VALUES (%s, %s, %s, %s)
                """,
                (publication_id, imagen_url, orden, es_principal),
            )
            image_id = cursor.lastrowid
            cursor.execute(
                """
                SELECT
                    id,
                    publicacion_id,
                    imagen_url,
                    orden,
                    es_principal
                FROM publicacion_imagenes
                WHERE id = %s
                """,
                (image_id,),
            )
            image = cursor.fetchone()

        connection.commit()
        return image
    except (ValueError, LookupError):
        if connection:
            connection.rollback()
        raise
    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error
    finally:
        if connection:
            connection.close()


def database_is_available() -> bool:
    connection = None

    try:
        connection = _connect()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() is not None
    except (PersistenceUnavailableError, pymysql.MySQLError):
        return False
    finally:
        if connection:
            connection.close()


def hide_publication(publication_id: int) -> bool:
    with transaction() as cursor:
        cursor.execute("SELECT id FROM publicaciones WHERE id = %s FOR UPDATE", (publication_id,))
        if cursor.fetchone() is None:
            return False
        cursor.execute("UPDATE publicaciones SET visible = FALSE WHERE id = %s", (publication_id,))
        return True


def _lock_owner(cursor, publication_id: int, owner_id: int) -> bool:
    cursor.execute("SELECT id FROM publicaciones WHERE id = %s AND propietario_id = %s FOR UPDATE", (publication_id, owner_id))
    return cursor.fetchone() is not None


def remove_publication_image(publication_id: int, owner_id: int, image_id: int) -> str | None:
    with transaction() as cursor:
        if not _lock_owner(cursor, publication_id, owner_id):
            return None
        cursor.execute("SELECT imagen_url, es_principal FROM publicacion_imagenes WHERE id = %s AND publicacion_id = %s", (image_id, publication_id))
        image = cursor.fetchone()
        if not image:
            return None
        cursor.execute("DELETE FROM publicacion_imagenes WHERE id = %s", (image_id,))
        if image["es_principal"]:
            cursor.execute("UPDATE publicacion_imagenes SET es_principal = TRUE WHERE publicacion_id = %s ORDER BY orden LIMIT 1", (publication_id,))
        return image["imagen_url"]


def set_primary_image(publication_id: int, owner_id: int, image_id: int) -> bool:
    with transaction() as cursor:
        if not _lock_owner(cursor, publication_id, owner_id):
            return False
        cursor.execute("SELECT id FROM publicacion_imagenes WHERE id = %s AND publicacion_id = %s", (image_id, publication_id))
        if cursor.fetchone() is None:
            return False
        cursor.execute("UPDATE publicacion_imagenes SET es_principal = (id = %s) WHERE publicacion_id = %s", (image_id, publication_id))
        return True


def list_publication_images_batch(publication_ids: list[int]) -> dict[int, list[dict]]:
    """Lectura de imágenes en lote; Publicaciones conserva SQL y sus datos."""
    ids = tuple(dict.fromkeys(publication_ids))
    if not ids:
        return {}
    initialize_database()
    connection = None
    grouped = {publication_id: [] for publication_id in ids}
    try:
        connection = _connect()
        with connection.cursor() as cursor:
            placeholders = ", ".join(["%s"] * len(ids))
            cursor.execute(
                f"""
                SELECT id, publicacion_id, imagen_url, orden, es_principal
                FROM publicacion_imagenes
                WHERE publicacion_id IN ({placeholders})
                ORDER BY publicacion_id, orden ASC
                """,
                ids,
            )
            for image in cursor.fetchall():
                grouped[image["publicacion_id"]].append(image)
        return grouped
    except pymysql.MySQLError as error:
        raise PersistenceUnavailableError("La persistencia está temporalmente no disponible.") from error
    finally:
        if connection:
            connection.close()
