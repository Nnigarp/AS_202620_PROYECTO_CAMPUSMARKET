from pydantic import BaseModel


class Universidad(BaseModel):
    id: int
    nombre: str
    sigla: str
    ciudad: str
