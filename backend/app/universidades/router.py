from fastapi import APIRouter
from pydantic import BaseModel

from .repository import listar_activas

router = APIRouter(prefix="/universidades", tags=["universidades"])


class Universidad(BaseModel):
    id: int
    nombre: str
    sigla: str
    ciudad: str


@router.get("", response_model=list[Universidad], operation_id="listarUniversidades")
def universidades():
    return listar_activas()
