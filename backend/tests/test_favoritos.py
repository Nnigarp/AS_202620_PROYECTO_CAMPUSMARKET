from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from backend.app.catalogo import service as catalogo
from backend.app.db import PersistenceUnavailableError, transaction
from backend.app.favoritos import router as favoritos_router
from backend.app.main import app
from backend.app.publicaciones.service import ocultar_publicacion


@pytest.fixture
def publicacion(cuentas, payload_publicacion):
    vendedor, _ = cuentas
    result = vendedor["client"].post("/publicaciones", json=payload_publicacion)
    assert result.status_code == 201
    return result.json()


@pytest.mark.parametrize("method,path", [("GET", "/favoritos"), ("PUT", "/favoritos/1"), ("DELETE", "/favoritos/1")])
def test_favoritos_exigen_sesion_antes_de_persistencia(method, path, monkeypatch):
    def forbidden(*args):
        raise AssertionError("Sin sesión no se debe acceder a Favoritos")
    monkeypatch.setattr(favoritos_router, "listar_favoritos", forbidden)
    monkeypatch.setattr(favoritos_router, "agregar_favorito", forbidden)
    monkeypatch.setattr(favoritos_router, "quitar_favorito", forbidden)
    assert TestClient(app).request(method, path).status_code == 401


def test_idempotencia_privacidad_y_persistencia_tras_logout(cuentas, publicacion):
    a, b = cuentas
    path = f'/favoritos/{publicacion["id"]}'
    assert a["client"].put(path).status_code == 204
    assert a["client"].put(path).status_code == 204
    # Ni body ni query permiten seleccionar una identidad ajena.
    assert b["client"].get("/favoritos", params={"usuario_id": a["usuario"]["id"]}).json() == []
    assert b["client"].delete(path, params={"usuario_id": a["usuario"]["id"]}).status_code == 204
    result = a["client"].get("/favoritos")
    assert [p["id"] for p in result.json()] == [publicacion["id"]]
    assert result.headers["cache-control"] == "no-store"
    assert a["client"].post("/usuarios/logout").status_code == 204
    assert a["client"].get("/favoritos").status_code == 401
    fresh = TestClient(app)
    login = fresh.post("/usuarios/login", json={"correo": a["correo"], "password": a["password"]})
    fresh.headers["Authorization"] = f'Bearer {login.json()["access_token"]}'
    assert [p["id"] for p in fresh.get("/favoritos").json()] == [publicacion["id"]]
    assert fresh.delete(path).status_code == 204
    assert fresh.delete(path).status_code == 204
    assert fresh.get("/favoritos").json() == []


def test_agregados_concurrentes_no_duplican(cuentas, publicacion):
    a, _ = cuentas
    def guardar(_):
        with TestClient(app) as client:
            return client.put(f'/favoritos/{publicacion["id"]}', headers={"Authorization": f'Bearer {a["token"]}'}).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(guardar, range(8))) == [204] * 8
    with transaction() as cursor:
        cursor.execute("SELECT COUNT(*) AS n FROM favoritos WHERE usuario_id = %s AND publicacion_id = %s",
                       (a["usuario"]["id"], publicacion["id"]))
        assert cursor.fetchone()["n"] == 1


def test_favoritos_no_muestran_ocultas_eliminadas_ni_inventan_disponibilidad(cuentas, publicacion):
    vendedor, comprador = cuentas
    id_ = publicacion["id"]
    path = f"/favoritos/{id_}"
    assert comprador["client"].put(path).status_code == 204
    assert vendedor["client"].patch(f"/publicaciones/{id_}/estado", json={"estado_publicacion": "vendido"}).status_code == 200
    assert comprador["client"].get("/favoritos").json()[0]["estado_publicacion"] == "vendido"
    assert ocultar_publicacion(id_)
    assert comprador["client"].get("/favoritos").json() == []
    assert comprador["client"].put(path).status_code == 404
    assert vendedor["client"].delete(f"/publicaciones/{id_}").status_code == 204
    assert comprador["client"].get("/favoritos").json() == []
    assert comprador["client"].put(path).status_code == 404
    assert comprador["client"].delete(path).status_code == 204


def test_imagenes_y_lecturas_se_componen_en_lote(monkeypatch):
    calls = []
    def publicaciones(ids):
        calls.append(("publicaciones", ids))
        return [{"id": 3}, {"id": 1}]
    def imagenes(ids):
        calls.append(("imagenes", ids))
        return {1: [{"id": 10}]}
    monkeypatch.setattr(catalogo, "listar_publicaciones_por_ids", publicaciones)
    monkeypatch.setattr(catalogo, "listar_imagenes_publicaciones", imagenes)
    assert catalogo.obtener_publicaciones_por_ids([1, 2, 3]) == [
        {"id": 1, "imagenes": [{"id": 10}]}, {"id": 3, "imagenes": []},
    ]
    assert calls == [("publicaciones", [1, 2, 3]), ("imagenes", [3, 1])]


def test_fallo_mysql_no_expone_detalles(monkeypatch):
    from backend.app.usuarios.dependencies import usuario_actual
    app.dependency_overrides[usuario_actual] = lambda: {"id": 7}
    def fallar(_):
        raise PersistenceUnavailableError("detalles internos no deben salir")
    monkeypatch.setattr(favoritos_router, "listar_favoritos", fallar)
    try:
        result = TestClient(app).get("/favoritos")
        assert result.status_code == 503
        assert "internos" not in result.text
    finally:
        app.dependency_overrides.clear()


def test_contrato_favoritos_es_privado_y_no_recibe_identidad():
    for path in ("/favoritos", "/favoritos/{publicacion_id}"):
        for operation in app.openapi()["paths"][path].values():
            assert operation["security"] == [{"HTTPBearer": []}]
            assert "requestBody" not in operation
            assert all(p["name"] != "usuario_id" for p in operation.get("parameters", []))
