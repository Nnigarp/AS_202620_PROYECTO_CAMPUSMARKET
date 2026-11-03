from typing import Literal

from pydantic import BaseModel, Field


class ImagenCatalogo(BaseModel):
    id: int
    publicacion_id: int
    imagen_url: str
    orden: int
    es_principal: bool


class PublicacionCatalogo(BaseModel):
    id: int
    titulo: str
    descripcion: str
    precio: float
    modalidad: Literal["venta", "alquiler"]
    estado: Literal["nuevo", "usado", "reacondicionado"]
    propietario_id: int | None = None
    universidad_id: int | None = None
    estado_publicacion: Literal["disponible", "reservado", "vendido"] = "disponible"
    imagenes: list[ImagenCatalogo] = Field(default_factory=list)


