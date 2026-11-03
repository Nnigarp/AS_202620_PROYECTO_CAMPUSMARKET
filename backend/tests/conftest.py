import os
import secrets
from io import BytesIO
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.administracion.repository import (
    initialize_database as init_administracion,
)
from backend.app.db import transaction
from backend.app.favoritos.repository import initialize_database as init_favoritos
from backend.app.main import app
from backend.app.mensajeria.repository import initialize_database as init_mensajeria
from backend.app.publicaciones.repository import (
    initialize_database as init_publicaciones,
)
from backend.app.usuarios.repository import initialize_database as init_usuarios


@pytest.fixture
def db_limpia():
    if not os.getenv("CAMPUSMARKET_DB_NAME", "").endswith("_test"):
        pytest.fail("Estas pruebas borran fixtures: requieren una base cuyo nombre termine en _test.")
    init_usuarios()
    init_publicaciones()
    init_administracion()
    init_favoritos()
    init_mensajeria()
    with transaction() as cursor:
        cursor.execute("DELETE FROM mensajes")
        cursor.execute("DELETE FROM conversaciones")
        cursor.execute("DELETE FROM favoritos")
        cursor.execute("DELETE FROM reportes_publicacion")
        cursor.execute("DELETE FROM publicaciones")
        cursor.execute("DELETE FROM sesiones_usuario")
        cursor.execute("DELETE FROM usuarios")
        cursor.execute("DELETE FROM intentos_autenticacion")


@pytest.fixture
def cuenta_factory(db_limpia):
    def crear(nombre="Estudiante"):
        client = TestClient(app)
        correo = f"{uuid4().hex}@campus.test"
        password = secrets.token_urlsafe(24)
        response = client.post("/usuarios/registro", json={"nombre": nombre, "correo": correo, "password": password})
        assert response.status_code == 201
        user = response.json()
        response = client.post("/usuarios/login", json={"correo": correo, "password": password})
        assert response.status_code == 200
        token = response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        return {"client": client, "usuario": user, "correo": correo, "password": password, "token": token}
    return crear


@pytest.fixture
def cuentas(cuenta_factory):
    return cuenta_factory("Usuario A"), cuenta_factory("Usuario B")


@pytest.fixture
def payload_publicacion():
    return {"titulo": "Calculadora científica", "descripcion": "Para cursos de ingeniería, en buen estado.", "precio": 65000, "modalidad": "venta", "estado": "usado"}


@pytest.fixture
def imagen_png():
    output = BytesIO()
    Image.new("RGB", (32, 24), color="#5B4CF0").save(output, format="PNG")
    return output.getvalue()
