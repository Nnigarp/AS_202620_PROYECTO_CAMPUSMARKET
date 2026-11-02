from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .dependencies import UsuarioActual, session_token
from .errors import AuthRateLimitError, DuplicateEmailError, InvalidCredentialsError
from .service import (
    editar_perfil,
    login,
    logout,
    registrar,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


class Credenciales(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)
    correo: str = Field(min_length=5, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    password: str = Field(min_length=12, max_length=128, repr=False)


class PerfilUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    nombre: str = Field(min_length=2, max_length=80)
    universidad_id: int | None = Field(default=None, ge=1)

    @field_validator("nombre")
    @classmethod
    def nombre_sin_controles(cls, value):
        if any(ord(character) < 32 for character in value):
            raise ValueError("El nombre contiene caracteres no permitidos.")
        return value


class Registro(Credenciales):
    nombre: str = Field(min_length=2, max_length=80)
    universidad_id: int | None = Field(default=None, ge=1)

    @field_validator("nombre", mode="before")
    @classmethod
    def normalizar_nombre(cls, value):
        return value.strip() if isinstance(value, str) else value


class Usuario(BaseModel):
    id: int
    nombre: str
    correo: str
    es_admin: bool
    universidad_id: int | None = None


class Sesion(BaseModel):
    access_token: str
    token_type: str
    expira_en: datetime
    usuario: Usuario


def _peer(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/registro", response_model=Usuario, status_code=201, operation_id="registrarUsuario")
def registro(payload: Registro, request: Request):
    try:
        return registrar(payload.nombre, payload.correo, payload.password, _peer(request), payload.universidad_id)
    except DuplicateEmailError as error:
        raise HTTPException(409, str(error)) from error
    except AuthRateLimitError as error:
        raise HTTPException(429, str(error), headers={"Retry-After": "300"}) from error
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@router.post("/login", response_model=Sesion, operation_id="iniciarSesion")
def iniciar_sesion(payload: Credenciales, request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        return login(payload.correo, payload.password, _peer(request))
    except InvalidCredentialsError as error:
        raise HTTPException(401, str(error), headers={"WWW-Authenticate": "Bearer"}) from error
    except AuthRateLimitError as error:
        raise HTTPException(429, str(error), headers={"Retry-After": "300"}) from error


@router.get("/me", response_model=Usuario, operation_id="consultarUsuarioActual")
def me(user: UsuarioActual):
    return user


@router.patch("/me", response_model=Usuario, operation_id="editarPerfil")
def perfil(payload: PerfilUpdate, user: UsuarioActual):
    try:
        universidad = user.get("universidad_id") if payload.universidad_id is None else payload.universidad_id
        return editar_perfil(user["id"], payload.nombre, universidad)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@router.post("/logout", status_code=204, operation_id="cerrarSesion")
def cerrar_sesion(user: UsuarioActual, token: Annotated[str, Depends(session_token)]):
    logout(token)
    return Response(status_code=204)
