from fastapi.testclient import TestClient
from backend.app.main import app


def test_catalogo_universidades_usa_api_publica(db_limpia):
    result = TestClient(app).get("/universidades")
    assert result.status_code == 200
    nombres = {row["nombre"] for row in result.json()}
    assert "Universidad de Cartagena" in nombres
    assert "Universidad Tecnológica de Bolívar" in nombres


def test_usuario_heredado_puede_completar_perfil(cuenta_factory):
    cuenta = cuenta_factory()
    client = cuenta["client"]
    assert client.get("/usuarios/me").json()["universidad_id"] is None
    result = client.patch("/usuarios/me", json={
        "nombre": "Estudiante", "universidad_id": 1,
    })
    assert result.status_code == 200
    assert result.json()["universidad_id"] == 1


def test_registro_universidad_valida_y_login(db_limpia):
    from uuid import uuid4

    client = TestClient(app)
    correo = f"universidad-{uuid4().hex}@gmail.com"
    password = "una-frase-de-contrasena-de-prueba"
    creado = client.post("/usuarios/registro", json={
        "nombre": "Estudiante UTB",
        "correo": correo,
        "password": password,
        "universidad_id": 1,
    })
    assert creado.status_code == 201
    assert creado.json()["universidad_id"] == 1

    sesion = client.post("/usuarios/login", json={"correo": correo, "password": password})
    assert sesion.status_code == 200
    assert sesion.json()["usuario"]["universidad_id"] == 1


def test_universidad_invalida_y_duplicado_conservan_codigos(db_limpia):
    from uuid import uuid4

    client = TestClient(app)
    payload = {
        "nombre": "Estudiante",
        "correo": f"prueba-{uuid4().hex}@gmail.com",
        "password": "una-frase-de-contrasena-de-prueba",
        "universidad_id": 99999,
    }
    assert client.post("/usuarios/registro", json=payload).status_code == 422
    payload["universidad_id"] = 1
    assert client.post("/usuarios/registro", json=payload).status_code == 201
    assert client.post("/usuarios/registro", json=payload).status_code == 409
