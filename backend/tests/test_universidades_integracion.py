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
