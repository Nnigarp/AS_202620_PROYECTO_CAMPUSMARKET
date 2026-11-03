from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.mensajeria import service
from backend.app.publicaciones.service import ocultar_publicacion


@pytest.fixture
def contexto(cuentas, cuenta_factory, payload_publicacion):
    vendedor, comprador = cuentas
    ajeno = cuenta_factory("Cuenta ajena")
    response = vendedor["client"].post("/publicaciones", json=payload_publicacion)
    assert response.status_code == 201
    publicacion = response.json()
    started = comprador["client"].post("/conversaciones", json={"publicacion_id": publicacion["id"]})
    assert started.status_code == 200
    return vendedor, comprador, ajeno, publicacion, started.json()


def mensaje(texto="Mensaje sintético de ensayo", clave=None):
    return {"texto": texto, "clave": clave or uuid4().hex}


def test_contexto_unico_no_autocontacto_ni_suplantacion(contexto):
    vendedor, comprador, _, publicacion, conversacion = contexto
    again = comprador["client"].post("/conversaciones", json={"publicacion_id": publicacion["id"]})
    assert again.json()["id"] == conversacion["id"]
    assert len(comprador["client"].get("/conversaciones").json()) == 1
    assert vendedor["client"].post("/conversaciones", json={"publicacion_id": publicacion["id"]}).status_code == 409
    for field in ("comprador_id", "vendedor_id", "usuario_id"):
        assert comprador["client"].post("/conversaciones", json={"publicacion_id": publicacion["id"], field: 123}).status_code == 422


def test_participantes_idempotencia_paginacion_y_persistencia(contexto):
    vendedor, comprador, _, _, conversacion = contexto
    path = f'/conversaciones/{conversacion["id"]}/mensajes'
    body = mensaje(" Hola desde el comprador ")
    first = comprador["client"].post(path, json=body)
    assert first.status_code == 201
    assert first.json()["texto"] == "Hola desde el comprador"
    assert first.json()["remitente_id"] == comprador["usuario"]["id"]
    assert first.json()["creado_en"].endswith("Z")
    assert comprador["client"].post(path, json=body).json()["id"] == first.json()["id"]
    assert comprador["client"].post(path, json={**body, "texto": "Distinto"}).status_code == 409
    second = vendedor["client"].post(path, json=mensaje("Respuesta del vendedor"))
    assert second.status_code == 201
    assert second.json()["remitente_id"] == vendedor["usuario"]["id"]
    for field in ("remitente_id", "usuario_id", "conversacion_id"):
        assert comprador["client"].post(path, json={**mensaje(), field: vendedor["usuario"]["id"]}).status_code == 422
    one = vendedor["client"].get(path, params={"limite": 1})
    assert one.headers["cache-control"] == "no-store"
    assert one.json()["hay_mas"]
    two = vendedor["client"].get(path, params={"despues_de": first.json()["id"], "limite": 1}).json()
    assert not two["hay_mas"]
    assert two["mensajes"][0]["id"] == second.json()["id"]
    inbox = comprador["client"].get("/conversaciones").json()[0]
    assert inbox["ultimo_mensaje"]["id"] == second.json()["id"]
    assert comprador["client"].post("/usuarios/logout").status_code == 204
    fresh = TestClient(app)
    login = fresh.post("/usuarios/login", json={"correo": comprador["correo"], "password": comprador["password"]})
    fresh.headers["Authorization"] = f'Bearer {login.json()["access_token"]}'
    assert len(fresh.get(path).json()["mensajes"]) == 2


def test_ajeno_no_puede_leer_enviar_ni_seleccionar_participante(contexto):
    vendedor, _, ajeno, _, conversacion = contexto
    path = f'/conversaciones/{conversacion["id"]}'
    assert ajeno["client"].get("/conversaciones", params={"usuario_id": vendedor["usuario"]["id"]}).json() == []
    assert ajeno["client"].get(path).status_code == 404
    assert ajeno["client"].get(path + "/mensajes").status_code == 404
    assert ajeno["client"].post(path + "/mensajes", json=mensaje(), params={"usuario_id": vendedor["usuario"]["id"]}).status_code == 404
    assert ajeno["client"].get("/conversaciones/9223372036854775807").json() == ajeno["client"].get(path).json()


def test_concurrencia_no_duplica_contexto_ni_mensaje(contexto):
    _, comprador, _, publicacion, conversacion = contexto
    headers = {"Authorization": f'Bearer {comprador["token"]}'}
    def iniciar(_):
        with TestClient(app) as client:
            return client.post("/conversaciones", headers=headers, json={"publicacion_id": publicacion["id"]}).json()["id"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(iniciar, range(6))) == [conversacion["id"]] * 6
    body = mensaje()
    def enviar(_):
        with TestClient(app) as client:
            result = client.post(f'/conversaciones/{conversacion["id"]}/mensajes', headers=headers, json=body)
            assert result.status_code == 201
            return result.json()["id"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert len(set(pool.map(enviar, range(6)))) == 1
    assert len(comprador["client"].get(f'/conversaciones/{conversacion["id"]}/mensajes').json()["mensajes"]) == 1


def test_oculta_conserva_historia_privada_sin_exponer_publicacion(contexto):
    vendedor, comprador, _, publicacion, conversacion = contexto
    path = f'/conversaciones/{conversacion["id"]}'
    assert comprador["client"].post(path + "/mensajes", json=mensaje()).status_code == 201
    assert ocultar_publicacion(publicacion["id"])
    assert comprador["client"].post("/conversaciones", json={"publicacion_id": publicacion["id"]}).status_code == 409
    assert comprador["client"].get(path).json()["publicacion"] is None
    assert vendedor["client"].get("/conversaciones").json()[0]["publicacion"] is None
    assert comprador["client"].post(path + "/mensajes", json=mensaje()).status_code == 409
    assert vendedor["client"].delete(f'/publicaciones/{publicacion["id"]}').status_code == 204
    assert len(comprador["client"].get(path + "/mensajes").json()["mensajes"]) == 1


@pytest.mark.parametrize("method,path,body", [
    ("GET", "/conversaciones", None), ("POST", "/conversaciones", {"publicacion_id": 1}),
    ("GET", "/conversaciones/1", None), ("GET", "/conversaciones/1/mensajes", None),
    ("POST", "/conversaciones/1/mensajes", mensaje()),
])
def test_todas_las_rutas_exigen_bearer(method, path, body):
    assert TestClient(app).request(method, path, json=body).status_code == 401
    operation = app.openapi()["paths"][path.replace("/1", "/{conversacion_id}")][method.lower()]
    assert operation["security"] == [{"HTTPBearer": []}]


def test_inbox_hidrata_publicaciones_en_lote(monkeypatch):
    calls = []
    monkeypatch.setattr(service, "list_for_user", lambda *_: [{"publicacion_id": 3}, {"publicacion_id": 3}, {"publicacion_id": 5}])
    def publicaciones(ids):
        calls.append(ids)
        return [{"id": 3}]
    monkeypatch.setattr(service, "obtener_publicaciones_por_ids", publicaciones)
    data = service.listar_conversaciones(1, 30, 0)
    assert calls == [[3, 5]]
    assert data[2]["publicacion"] is None


@pytest.mark.parametrize("texto", ["", "  \n  ", "x" * 2001])
def test_rechaza_texto_vacio_o_excesivo_antes_de_servicio(monkeypatch, texto):
    from backend.app.usuarios.dependencies import usuario_actual
    app.dependency_overrides[usuario_actual] = lambda: {"id": 7}
    def prohibido(*_):
        raise AssertionError("No debe llegar a servicio")
    monkeypatch.setattr("backend.app.mensajeria.router.enviar_mensaje", prohibido)
    try:
        assert TestClient(app).post("/conversaciones/1/mensajes", json=mensaje(texto)).status_code == 422
    finally:
        app.dependency_overrides.clear()
