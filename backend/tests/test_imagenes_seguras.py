from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import pytest
from PIL import Image, PngImagePlugin

from backend.app.publicaciones.image_storage import UPLOAD_ROOT


def _upload(client, publication_id, content, name="foto.png"):
    return client.post(f"/publicaciones/{publication_id}/imagenes", files={"archivo": (name, content, "image/png")})


def test_tres_imagenes_galeria_principal_eliminar_y_reponer(cuentas, payload_publicacion, imagen_png):
    a, b = cuentas
    client = a["client"]
    publication = client.post("/publicaciones", json=payload_publicacion).json()
    images = []
    for _ in range(3):
        response = _upload(client, publication["id"], imagen_png)
        assert response.status_code == 201
        images.append(response.json())
    assert _upload(client, publication["id"], imagen_png).status_code == 400
    assert len(b["client"].get(f"/catalogo/{publication['id']}").json()["imagenes"]) == 3
    response = client.put(f"/publicaciones/{publication['id']}/imagenes/{images[2]['id']}/principal")
    assert response.status_code == 200
    assert [image["id"] for image in response.json() if image["es_principal"]] == [images[2]["id"]]
    assert b["client"].delete(f"/publicaciones/{publication['id']}/imagenes/{images[2]['id']}").status_code == 404
    assert b["client"].put(f"/publicaciones/{publication['id']}/imagenes/{images[1]['id']}/principal").status_code == 404
    assert client.delete(f"/publicaciones/{publication['id']}/imagenes/{images[2]['id']}").status_code == 204
    assert sum(image["es_principal"] for image in client.get("/publicaciones/mias").json()[0]["imagenes"]) == 1
    assert _upload(client, publication["id"], imagen_png).status_code == 201
    for image in client.get("/publicaciones/mias").json()[0]["imagenes"]:
        response = client.get(image["imagen_url"])
        assert response.status_code == 200
        Image.open(BytesIO(response.content)).load()
    assert client.delete(f"/publicaciones/{publication['id']}").status_code == 204
    assert not list((UPLOAD_ROOT / str(publication["id"])).glob("*"))


@pytest.mark.parametrize(
    "content,name",
    [
        pytest.param(b"texto con extension falsa", "foto.png", id="contenido-invalido"),
        pytest.param(b"", "foto.png", id="archivo-vacio"),
        pytest.param(b"fake", "foto.svg", id="formato-svg"),
        pytest.param(b"x" * (5 * 1024 * 1024 + 1), "foto.jpg", id="excede-cinco-mib"),
    ],
)
def test_no_guarda_archivo_invalido(cuentas, payload_publicacion, content, name):
    a, _ = cuentas
    publication = a["client"].post("/publicaciones", json=payload_publicacion).json()
    assert _upload(a["client"], publication["id"], content, name).status_code == 400
    assert a["client"].get("/publicaciones/mias").json()[0]["imagenes"] == []


def test_contenido_no_puede_disfrazarse_con_otra_extension(cuentas, payload_publicacion, imagen_png):
    a, _ = cuentas
    publication = a["client"].post("/publicaciones", json=payload_publicacion).json()
    assert _upload(a["client"], publication["id"], imagen_png, "foto.jpg").status_code == 400


def test_reencodificacion_elimina_metadatos(cuentas, payload_publicacion):
    a, _ = cuentas
    publication = a["client"].post("/publicaciones", json=payload_publicacion).json()
    output = BytesIO()
    info = PngImagePlugin.PngInfo()
    info.add_text("private-location", "ubicacion-que-no-debe-publicarse")
    Image.new("RGB", (8, 8)).save(output, format="PNG", pnginfo=info)
    response = _upload(a["client"], publication["id"], output.getvalue())
    assert response.status_code == 201
    downloaded = a["client"].get(response.json()["imagen_url"])
    assert b"ubicacion-que-no-debe-publicarse" not in downloaded.content
    assert "private-location" not in Image.open(BytesIO(downloaded.content)).info


def test_subidas_concurrentes_no_superan_tres(cuentas, payload_publicacion, imagen_png):
    a, _ = cuentas
    publication = a["client"].post("/publicaciones", json=payload_publicacion).json()
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda _: _upload(a["client"], publication["id"], imagen_png), range(4)))
    assert sorted(response.status_code for response in responses) == [201, 201, 201, 400]
    images = a["client"].get("/publicaciones/mias").json()[0]["imagenes"]
    assert len(images) == 3
    assert len({image["orden"] for image in images}) == 3
    assert sum(image["es_principal"] for image in images) == 1
    assert len(list((UPLOAD_ROOT / str(publication["id"])).glob("*"))) == 3


def test_fotografia_grande_se_normaliza_sin_perder_formato(cuentas, payload_publicacion):
    a, _ = cuentas
    publication = a["client"].post("/publicaciones", json=payload_publicacion).json()
    output = BytesIO()
    Image.new("RGB", (4000, 3000), "#615599").save(output, format="PNG")
    response = _upload(a["client"], publication["id"], output.getvalue())
    assert response.status_code == 201
    downloaded = a["client"].get(response.json()["imagen_url"])
    image = Image.open(BytesIO(downloaded.content))
    image.load()
    assert image.size == (2048, 1536)
    assert image.format == "PNG"


def test_orientacion_de_camara_se_conserva_al_retirar_exif(cuentas, payload_publicacion):
    a, _ = cuentas
    publication = a["client"].post("/publicaciones", json=payload_publicacion).json()
    output = BytesIO()
    exif = Image.Exif()
    exif[274] = 6
    Image.new("RGB", (100, 60), "#615599").save(output, format="JPEG", exif=exif)
    response = _upload(a["client"], publication["id"], output.getvalue(), "camara.jpg")
    assert response.status_code == 201
    downloaded = a["client"].get(response.json()["imagen_url"])
    image = Image.open(BytesIO(downloaded.content))
    assert image.size == (60, 100)
    assert not image.getexif()
