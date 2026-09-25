import os

import pymysql
from pymysql.cursors import DictCursor


class PersistenceUnavailableError(RuntimeError):
    """La persistencia no está disponible temporalmente."""


def _connect():
    try:
        return pymysql.connect(
            host=os.getenv("CAMPUSMARKET_DB_HOST", "localhost"),
            port=int(os.getenv("CAMPUSMARKET_DB_PORT", "3306")),
            user=os.getenv("CAMPUSMARKET_DB_USER", "campusmarket_app"),
            password=os.getenv("CAMPUSMARKET_DB_PASSWORD", ""),
            database=os.getenv("CAMPUSMARKET_DB_NAME", "campusmarket"),
            cursorclass=DictCursor,
            autocommit=False,
            connect_timeout=2,
        )
    except pymysql.MySQLError as error:
        raise PersistenceUnavailableError(
            "La persistencia está temporalmente no disponible."
        ) from error


def initialize_database() -> None:
    connection = None

    try:
        connection = _connect()

        with connection.cursor() as cursor:
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
                    PRIMARY KEY (id),
                    CONSTRAINT chk_publicaciones_precio
                        CHECK (precio > 0)
                )
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


def create_publication(data: dict) -> dict:
    initialize_database()

    connection = None

    try:
        connection = _connect()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO publicaciones (
                    titulo,
                    descripcion,
                    precio,
                    modalidad,
                    estado
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    data["titulo"],
                    data["descripcion"],
                    data["precio"],
                    data["modalidad"],
                    data["estado"],
                ),
            )

            publication_id = cursor.lastrowid

            cursor.execute(
                """
                SELECT
                    id,
                    titulo,
                    descripcion,
                    CAST(precio AS DOUBLE) AS precio,
                    modalidad,
                    estado
                FROM publicaciones
                WHERE id = %s
                """,
                (publication_id,),
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


def list_publications() -> list[dict]:
    initialize_database()

    connection = None

    try:
        connection = _connect()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    titulo,
                    descripcion,
                    CAST(precio AS DOUBLE) AS precio,
                    modalidad,
                    estado
                FROM publicaciones
                ORDER BY id DESC
                """
            )

            rows = cursor.fetchall()

        return rows

    except pymysql.MySQLError as error:
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
