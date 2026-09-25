from fastapi.testclient import TestClient

from backend.app import main as main_module

client = TestClient(main_module.app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "campusmarket-api",
    }


def test_health_check_reporta_fallo_de_persistencia(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "database_is_available",
        lambda: False,
    )

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "service": "campusmarket-api",
    }
