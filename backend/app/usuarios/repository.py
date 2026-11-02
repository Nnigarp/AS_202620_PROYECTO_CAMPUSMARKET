import pymysql

from backend.app.db import transaction
from backend.app.universidades.repository import initialize_database as init_universidades

from .errors import DuplicateEmailError


def initialize_database() -> None:
    init_universidades()
    with transaction() as cursor:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(80) NOT NULL,
                correo VARCHAR(254) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            SELECT 1 FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'usuarios' AND COLUMN_NAME = 'universidad_id'
        """)
        if cursor.fetchone() is None:
            cursor.execute("""
                ALTER TABLE usuarios ADD COLUMN universidad_id BIGINT UNSIGNED NULL,
                ADD CONSTRAINT fk_usuarios_universidad FOREIGN KEY (universidad_id)
                    REFERENCES universidades(id)
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones_usuario (
                token_hash CHAR(64) NOT NULL PRIMARY KEY,
                usuario_id BIGINT UNSIGNED NOT NULL,
                expira_en DATETIME NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                INDEX idx_sesiones_expiracion (expira_en)
            ) ENGINE=InnoDB
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intentos_autenticacion (
                clave CHAR(64) NOT NULL PRIMARY KEY,
                intentos INT NOT NULL,
                reinicia_en DATETIME NOT NULL
            ) ENGINE=InnoDB
        """)


def create_user(nombre: str, correo: str, password_hash: str, universidad_id: int | None = None) -> dict:
    initialize_database()
    with transaction() as cursor:
        try:
            cursor.execute(
                "INSERT INTO usuarios (nombre, correo, password_hash, universidad_id) VALUES (%s, %s, %s, %s)",
                (nombre, correo, password_hash, universidad_id),
            )
        except pymysql.IntegrityError as error:
            if error.args[0] == 1062:
                raise DuplicateEmailError("El correo ya está registrado.") from error
            raise
        user_id = cursor.lastrowid
    return {"id": user_id, "nombre": nombre, "correo": correo, "universidad_id": universidad_id}


def find_user(correo: str) -> dict | None:
    initialize_database()
    with transaction() as cursor:
        cursor.execute("SELECT id, nombre, correo, password_hash, universidad_id FROM usuarios WHERE correo = %s", (correo,))
        return cursor.fetchone()


def create_session(token_hash: str, user_id: int, expires) -> None:
    with transaction() as cursor:
        cursor.execute("DELETE FROM sesiones_usuario WHERE expira_en <= UTC_TIMESTAMP()")
        cursor.execute(
            "INSERT INTO sesiones_usuario (token_hash, usuario_id, expira_en) VALUES (%s, %s, %s)",
            (token_hash, user_id, expires),
        )


def session_user(token_hash: str) -> dict | None:
    initialize_database()
    with transaction() as cursor:
        cursor.execute("""
            SELECT u.id, u.nombre, u.correo, u.universidad_id
            FROM sesiones_usuario s JOIN usuarios u ON u.id = s.usuario_id
            WHERE s.token_hash = %s AND s.expira_en > UTC_TIMESTAMP()
        """, (token_hash,))
        return cursor.fetchone()


def revoke_session(token_hash: str) -> None:
    with transaction() as cursor:
        cursor.execute("DELETE FROM sesiones_usuario WHERE token_hash = %s", (token_hash,))


def update_profile(user_id: int, nombre: str, universidad_id: int | None = None) -> dict:
    with transaction() as cursor:
        cursor.execute("UPDATE usuarios SET nombre = %s, universidad_id = %s WHERE id = %s", (nombre, universidad_id, user_id))
        cursor.execute("SELECT id, nombre, correo, universidad_id FROM usuarios WHERE id = %s", (user_id,))
        return cursor.fetchone()


def consume_auth_budget(key: str, maximum: int) -> bool:
    """Ventana persistente de cinco minutos, serializada por clave en MySQL."""
    initialize_database()
    with transaction() as cursor:
        cursor.execute("DELETE FROM intentos_autenticacion WHERE reinicia_en <= UTC_TIMESTAMP()")
        cursor.execute("""
            INSERT INTO intentos_autenticacion (clave, intentos, reinicia_en)
            VALUES (%s, 1, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 5 MINUTE))
            ON DUPLICATE KEY UPDATE intentos = intentos + 1
        """, (key,))
        cursor.execute("SELECT intentos FROM intentos_autenticacion WHERE clave = %s", (key,))
        return cursor.fetchone()["intentos"] <= maximum
