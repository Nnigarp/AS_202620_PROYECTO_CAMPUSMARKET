from fastapi import APIRouter

from .schemas import Universidad
from .service import listar_universidades

router = APIRouter(prefix="/universidades", tags=["universidades"])


@router.get("", response_model=list[Universidad], operation_id="listarUniversidades")
def universidades():
    return listar_universidades()
