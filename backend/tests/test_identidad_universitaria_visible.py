from pathlib import Path

from backend.app.catalogo import service
from backend.app.db import transaction


def test_metadata_declara_institucion_al_publicar_no_perfil_actual(cuentas, payload_publicacion):
    vendedor, lector = cuentas
    assert vendedor["client"].patch("/usuarios/me", json={"nombre": "Autor de prueba", "universidad_id": 1}).status_code == 200
    created = vendedor["client"].post("/publicaciones", json=payload_publicacion).json()
    assert vendedor["client"].patch("/usuarios/me", json={"nombre": "Autor de prueba", "universidad_id": 2}).status_code == 200
    detail = lector["client"].get(f'/catalogo/{created["id"]}').json()
    assert detail["universidad_id"] == detail["universidad"]["id"] == 1
    assert detail["universidad"]["sigla"] == "UTB"
    assert detail["universidad"]["nombre"] == "Universidad Tecnológica de Bolívar"
    assert lector["client"].get("/catalogo?universidad_id=1").json()[0]["universidad"]["id"] == 1
    assert lector["client"].get("/catalogo?universidad_id=2").json() == []
    assert lector["client"].put(f'/favoritos/{created["id"]}').status_code == 204
    assert lector["client"].get("/favoritos").json()[0]["universidad"]["sigla"] == "UTB"


def test_heredada_sin_institucion_no_se_infiere_desde_el_perfil(cuentas, payload_publicacion):
    vendedor, lector = cuentas
    created = vendedor["client"].post("/publicaciones", json=payload_publicacion).json()
    assert vendedor["client"].patch("/usuarios/me", json={"nombre": "Autor de prueba", "universidad_id": 1}).status_code == 200
    detail = lector["client"].get(f'/catalogo/{created["id"]}').json()
    assert detail["universidad_id"] is None
    assert detail["universidad"] is None
    assert len(lector["client"].get("/catalogo").json()) == 1
    assert lector["client"].get("/catalogo?universidad_id=1").json() == []


def test_institucion_inactiva_no_borra_identidad_historica(cuentas, payload_publicacion):
    vendedor, lector = cuentas
    vendedor["client"].patch("/usuarios/me", json={"nombre": "Autor de prueba", "universidad_id": 1})
    id_ = vendedor["client"].post("/publicaciones", json=payload_publicacion).json()["id"]
    try:
        with transaction() as cursor:
            cursor.execute("UPDATE universidades SET activa = FALSE WHERE id = 1")
        detail = lector["client"].get(f"/catalogo/{id_}").json()
        assert detail["universidad"]["id"] == 1
        assert all(u["id"] != 1 for u in lector["client"].get("/universidades").json())
    finally:
        with transaction() as cursor:
            cursor.execute("UPDATE universidades SET activa = TRUE WHERE id = 1")


def test_mil_publicaciones_hidratan_universidades_e_imagenes_una_vez(monkeypatch):
    publications = [{"id": id_, "universidad_id": None if id_ == 1 else 1 if id_ % 2 else 2}
                    for id_ in range(1, 1001)]
    calls = []
    monkeypatch.setattr(service, "listar_publicaciones", lambda: publications)
    def imagenes(ids):
        calls.append(("imagenes", len(ids)))
        return {}
    def universidades(ids):
        calls.append(("universidades", ids))
        return {1: {"id": 1, "sigla": "UTB"}, 2: {"id": 2, "sigla": "UdeC"}}
    monkeypatch.setattr(service, "listar_imagenes_publicaciones", imagenes)
    monkeypatch.setattr(service, "obtener_universidades_por_ids", universidades)
    result = service.buscar_publicaciones()
    assert len(result) == 1000
    assert result[0]["universidad"] is None
    assert result[1]["universidad"]["sigla"] == "UdeC"
    assert calls == [("imagenes", 1000), ("universidades", [1, 2])]


def test_catalogo_solo_usa_capacidad_publica_de_universidades():
    catalogo = Path(__file__).resolve().parents[1] / "app" / "catalogo"
    source = "\n".join(p.read_text() for p in catalogo.glob("*.py"))
    assert "universidades.service" in source
    assert "universidades.repository" not in source
    assert "app.db" not in source
