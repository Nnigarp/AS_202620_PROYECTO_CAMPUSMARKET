import json

from fastapi.testclient import TestClient

from backend.app import main as main_module
from backend.app import observability as observability_module


client = TestClient(main_module.app)


def test_log_http_estructurado_y_request_id(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "database_is_available",
        lambda: True,
    )

    log_messages = []

    monkeypatch.setattr(
        observability_module.logger,
        "info",
        log_messages.append,
    )

    response = client.get(
        "/health",
        headers={"X-Request-ID": "s8-test-request-id"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "s8-test-request-id"

    assert log_messages

    log_entry = json.loads(log_messages[-1])

    assert log_entry["level"] == "INFO"
    assert log_entry["event"] == "http_request"
    assert log_entry["request_id"] == "s8-test-request-id"
    assert log_entry["method"] == "GET"
    assert log_entry["path"] == "/health"
    assert log_entry["status_code"] == 200
    assert log_entry["duration_ms"] >= 0
    assert log_entry["timestamp"]
