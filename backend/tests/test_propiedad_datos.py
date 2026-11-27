import ast
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"
OWNERS = {
    "conversaciones": "mensajeria",
    "favoritos": "favoritos",
    "intentos_autenticacion": "usuarios",
    "mensajes": "mensajeria",
    "publicacion_imagenes": "publicaciones",
    "publicaciones": "publicaciones",
    "reportes_publicacion": "administracion",
    "sesiones_usuario": "usuarios",
    "solicitudes_idempotentes": "publicaciones",
    "universidades": "universidades",
    "usuarios": "usuarios",
}
WRITE = re.compile(r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+([a-z_]+)\b", re.IGNORECASE)


def escrituras_ajenas(app):
    violations = []
    for path in app.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for table in WRITE.findall(node.value):
                    owner = OWNERS.get(table.lower())
                    if owner and path != app / owner / "repository.py":
                        violations.append((path.relative_to(app).as_posix(), table.lower()))
    return violations


def test_cada_tabla_solo_tiene_escritor_en_su_repository():
    assert not escrituras_ajenas(APP)


def test_guarda_distingue_el_propietario_de_solicitudes_idempotentes(tmp_path):
    for contexto in ("publicaciones", "catalogo"):
        modulo = tmp_path / contexto
        modulo.mkdir()
        (modulo / "repository.py").write_text(
            'SQL = "UPDATE solicitudes_idempotentes SET publicacion_id = %s"'
        )
    assert escrituras_ajenas(tmp_path) == [("catalogo/repository.py", "solicitudes_idempotentes")]


def test_ningun_contexto_importa_repository_ajeno_incluso_por_alias():
    violations = []
    for owner in ("usuarios", "publicaciones", "catalogo", "administracion", "favoritos", "mensajeria", "universidades"):
        for path in (APP / owner).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [f"{node.module}.{alias.name}" for alias in node.names] if node.module else []
                for name in names:
                    for foreign in OWNERS.values():
                        if foreign != owner and f"{foreign}.repository" in name:
                            violations.append(str(path.relative_to(APP)))
    assert not violations


def test_routers_y_services_no_acceden_a_conexion_sql():
    violations = []
    for path in APP.rglob("*.py"):
        if path.name not in {"router.py", "service.py"}:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module in {"backend.app.db", "pymysql"}:
                violations.append(str(path.relative_to(APP)))
            if isinstance(node, ast.Import) and any(alias.name == "pymysql" for alias in node.names):
                violations.append(str(path.relative_to(APP)))
    assert not violations
