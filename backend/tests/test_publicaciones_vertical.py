from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.publicaciones.repository import (
    _connect,
    initialize_database,
)

client = TestClient(app)


def _limpiar_publicaciones():
    initialize_database()

    connection = _connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM publicaciones")

        connection.commit()

    finally:
        connection.close()


def test_corte_vertical_crea_y_recupera_publicacion():
    _limpiar_publicaciones()

    payload = {
        "titulo": "Calculadora científica",
        "descripcion": "Calculadora reacondicionada en buen estado",
        "precio": 65000,
        "modalidad": "venta",
        "estado": "reacondicionado",
    }

    create_response = client.post(
        "/publicaciones",
        json=payload,
    )

    assert create_response.status_code == 201

    created = create_response.json()

    assert created["id"] > 0
    assert created["titulo"] == payload["titulo"]
    assert created["estado"] == "reacondicionado"

    list_response = client.get("/publicaciones")

    assert list_response.status_code == 200

    publicaciones = list_response.json()

    assert len(publicaciones) == 1
    assert publicaciones[0] == created
    assert publicaciones[0]["estado"] == "reacondicionado"


def test_mysql_persiste_y_recupera_publicacion():
    _limpiar_publicaciones()

    payload = {
        "titulo": "Libro arquitectura",
        "descripcion": "Persistencia verificada sobre MySQL",
        "precio": 50000,
        "modalidad": "venta",
        "estado": "usado",
    }

    response = client.post(
        "/publicaciones",
        json=payload,
    )

    assert response.status_code == 201

    created = response.json()

    connection = _connect()

    try:
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
                WHERE id = %s
                """,
                (created["id"],),
            )

            row = cursor.fetchone()

    finally:
        connection.close()

    assert row is not None
    assert row["id"] == created["id"]
    assert row["titulo"] == payload["titulo"]
    assert row["estado"] == payload["estado"]


def test_mysql_indisponible_degrada_controladamente(
    monkeypatch,
):
    monkeypatch.setenv(
        "CAMPUSMARKET_DB_PORT",
        "3399",
    )

    payload = {
        "titulo": "Prueba indisponibilidad",
        "descripcion": "MySQL temporalmente no disponible",
        "precio": 50000,
        "modalidad": "venta",
        "estado": "usado",
    }

    response = client.post(
        "/publicaciones",
        json=payload,
    )

    assert response.status_code == 503

    detail = response.json()["detail"]

    assert "temporalmente no disponible" in detail.lower()