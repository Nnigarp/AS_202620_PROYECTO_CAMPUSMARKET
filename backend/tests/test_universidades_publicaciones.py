"""Asociación declarativa de universidad y filtros del catálogo."""
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_publicacion_guarda_universidad_del_autor(cuentas, payload_publicacion):
    autor, lector = cuentas
    perfil = autor["client"].patch(
        "/usuarios/me",
        json={"nombre": autor["usuario"]["nombre"], "universidad_id": 1},
    )
    assert perfil.status_code == 200
    publicada = autor["client"].post("/publicaciones", json=payload_publicacion)
    assert publicada.status_code == 201
    assert publicada.json()["universidad_id"] == 1

    detalle = lector["client"].get(f"/catalogo/{publicada.json()['id']}")
    assert detalle.status_code == 200
    assert detalle.json()["universidad_id"] == 1

    filtradas = client.get("/catalogo", params={"universidad_id": 1})
    assert filtradas.status_code == 200
    assert publicada.json()["id"] in [p["id"] for p in filtradas.json()]

    otras = client.get("/catalogo", params={"universidad_id": 2})
    assert otras.status_code == 200
    assert publicada.json()["id"] not in [p["id"] for p in otras.json()]


def test_publicacion_legacy_sin_universidad_es_visible_en_toda_cartagena(cuentas, payload_publicacion):
    autor, _ = cuentas
    publicada = autor["client"].post("/publicaciones", json=payload_publicacion)
    assert publicada.status_code == 201
    assert publicada.json()["universidad_id"] is None
    todas = client.get("/catalogo")
    assert todas.status_code == 200
    assert publicada.json()["id"] in [p["id"] for p in todas.json()]
    filtradas = client.get("/catalogo", params={"universidad_id": 1})
    assert publicada.json()["id"] not in [p["id"] for p in filtradas.json()]


def test_catalogo_rechaza_id_universidad_invalido():
    assert client.get("/catalogo", params={"universidad_id": 0}).status_code == 422
    assert client.get("/catalogo", params={"universidad_id": "ninguna"}).status_code == 422


def test_cambiar_universidad_perfil_no_reasigna_publicaciones(cuentas, payload_publicacion):
    """La universidad queda fijada en cada publicación en el momento del alta."""
    autor, otro = cuentas
    asignar_utb = autor["client"].patch(
        "/usuarios/me",
        json={"nombre": autor["usuario"]["nombre"], "universidad_id": 1},
    )
    assert asignar_utb.status_code == 200

    primera = autor["client"].post("/publicaciones", json=payload_publicacion)
    assert primera.status_code == 201
    primera_id = primera.json()["id"]
    assert primera.json()["universidad_id"] == 1

    cambio = autor["client"].patch(
        "/usuarios/me",
        json={"nombre": autor["usuario"]["nombre"], "universidad_id": 2},
    )
    assert cambio.status_code == 200
    assert cambio.json()["universidad_id"] == 2

    detalle_anterior = otro["client"].get(f"/catalogo/{primera_id}")
    assert detalle_anterior.status_code == 200
    assert detalle_anterior.json()["universidad_id"] == 1

    segunda = autor["client"].post("/publicaciones", json={
        **payload_publicacion, "titulo": "Publicación creada después del cambio",
    })
    assert segunda.status_code == 201
    segunda_id = segunda.json()["id"]
    assert segunda.json()["universidad_id"] == 2

    utb = otro["client"].get("/catalogo", params={"universidad_id": 1})
    udec = otro["client"].get("/catalogo", params={"universidad_id": 2})
    assert utb.status_code == udec.status_code == 200
    assert primera_id in {item["id"] for item in utb.json()}
    assert segunda_id not in {item["id"] for item in utb.json()}
    assert segunda_id in {item["id"] for item in udec.json()}
    assert primera_id not in {item["id"] for item in udec.json()}
