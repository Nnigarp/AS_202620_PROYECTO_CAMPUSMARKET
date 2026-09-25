from fastapi.testclient import TestClient

from backend.app import main as main_module
from backend.app import observability as observability_module

client = TestClient(main_module.app)


def test_ec01_metric_inicia_sin_evaluacion():
    observability_module.reset_ec01_metric()

    response = client.get("/ops/metrics/ec01")

    assert response.status_code == 200

    metric = response.json()

    assert metric["scenario_id"] == "EC-01"
    assert metric["quality_attribute"] == "rendimiento"
    assert metric["measurement_scope"] == "backend GET /publicaciones"
    assert metric["window_size"] == 10
    assert metric["threshold_ms"] == 2000.0
    assert metric["required_within_threshold"] == 9
    assert metric["observed_requests"] == 0
    assert metric["within_threshold"] == 0
    assert metric["evaluation_available"] is False
    assert metric["meets_backend_target"] is None
    assert metric["ec01_fully_verified"] is False
    assert metric["samples"] == []

    observability_module.reset_ec01_metric()


def test_ec01_metric_cumple_objetivo_backend_con_9_de_10():
    observability_module.reset_ec01_metric()

    for _ in range(9):
        observability_module._record_ec01_measurement(
            method="GET",
            path="/publicaciones",
            status_code=200,
            duration_ms=150.0,
        )

    observability_module._record_ec01_measurement(
        method="GET",
        path="/publicaciones",
        status_code=200,
        duration_ms=2500.0,
    )

    metric = observability_module.get_ec01_metric()

    assert metric["observed_requests"] == 10
    assert metric["within_threshold"] == 9
    assert metric["evaluation_available"] is True
    assert metric["meets_backend_target"] is True
    assert metric["ec01_fully_verified"] is False

    observability_module.reset_ec01_metric()


def test_ec01_metric_no_cumple_objetivo_backend_con_8_de_10():
    observability_module.reset_ec01_metric()

    for _ in range(8):
        observability_module._record_ec01_measurement(
            method="GET",
            path="/publicaciones",
            status_code=200,
            duration_ms=150.0,
        )

    for _ in range(2):
        observability_module._record_ec01_measurement(
            method="GET",
            path="/publicaciones",
            status_code=503,
            duration_ms=100.0,
        )

    metric = observability_module.get_ec01_metric()

    assert metric["observed_requests"] == 10
    assert metric["within_threshold"] == 8
    assert metric["evaluation_available"] is True
    assert metric["meets_backend_target"] is False
    assert metric["ec01_fully_verified"] is False

    observability_module.reset_ec01_metric()
