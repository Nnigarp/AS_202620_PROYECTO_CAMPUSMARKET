import json
from pathlib import Path

from backend.app.main import app

CONTRACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "openapi-v1.json"
)


def _load_versioned_contract() -> dict:
    with CONTRACT_PATH.open(encoding="utf-8") as contract_file:
        return json.load(contract_file)


def test_contrato_openapi_es_ejecutable_y_versionado():
    contract = _load_versioned_contract()

    assert contract["openapi"] == "3.1.0"
    assert contract["info"]["version"] == "1.0.0"
    assert contract["paths"]
    assert contract["components"]["schemas"]


def test_proveedor_fastapi_cumple_el_contrato_versionado():
    contract = _load_versioned_contract()
    provider_schema = app.openapi()

    assert provider_schema == contract, (
        "La API implementada ya no coincide con contracts/openapi-v1.json. "
        "Un cambio del proveedor modificó rutas, operaciones o esquemas sin "
        "evolucionar primero el contrato."
    )


def test_contrato_v1_preserva_necesidades_del_consumidor_flutter():
    contract = _load_versioned_contract()
    publications = contract["paths"]["/publicaciones"]
    create_schema = contract["components"]["schemas"]["PublicacionCreate"]
    publication_schema = contract["components"]["schemas"]["Publicacion"]

    assert publications["post"]["operationId"] == "crearPublicacion"
    assert publications["get"]["operationId"] == "listarPublicaciones"
    assert set(create_schema["required"]) == {
        "titulo",
        "descripcion",
        "precio",
        "modalidad",
        "estado",
    }
    assert set(publication_schema["required"]) == {
        *create_schema["required"],
        "id",
    }
    assert {"201", "422", "503"} <= set(
        publications["post"]["responses"]
    )
