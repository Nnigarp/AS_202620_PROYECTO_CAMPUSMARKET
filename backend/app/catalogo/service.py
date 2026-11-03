from backend.app.publicaciones.service import (
    listar_imagenes_publicacion,
    listar_imagenes_publicaciones,
    listar_publicaciones,
)


def _con_imagenes(publicacion: dict) -> dict:
    publicacion_id = int(publicacion["id"])

    return {
        **publicacion,
        "imagenes": listar_imagenes_publicacion(publicacion_id),
    }


def buscar_publicaciones(
    texto: str | None = None,
    modalidad: str | None = None,
    estado: str | None = None,
    precio_min: float | None = None,
    precio_max: float | None = None,
    universidad_id: int | None = None,
) -> list[dict]:
    publicaciones = listar_publicaciones()

    texto_normalizado = texto.strip().lower() if texto else None

    resultado = []

    for publicacion in publicaciones:
        if universidad_id is not None and publicacion.get("universidad_id") != universidad_id:
            continue

        if texto_normalizado:
            titulo = str(publicacion.get("titulo", "")).lower()
            descripcion = str(publicacion.get("descripcion", "")).lower()

            if (
                texto_normalizado not in titulo
                and texto_normalizado not in descripcion
            ):
                continue

        if modalidad and publicacion.get("modalidad") != modalidad:
            continue

        if estado and publicacion.get("estado") != estado:
            continue

        precio = float(publicacion.get("precio", 0))

        if precio_min is not None and precio < precio_min:
            continue

        if precio_max is not None and precio > precio_max:
            continue

        resultado.append(publicacion)

    ids = [int(publicacion["id"]) for publicacion in resultado]
    imagenes_por_publicacion = listar_imagenes_publicaciones(ids)
    return [
        {**publicacion, "imagenes": imagenes_por_publicacion.get(int(publicacion["id"]), [])}
        for publicacion in resultado
    ]


def obtener_publicacion(publicacion_id: int) -> dict | None:
    publicaciones = listar_publicaciones()

    for publicacion in publicaciones:
        if int(publicacion["id"]) == publicacion_id:
            return _con_imagenes(publicacion)

    return None
