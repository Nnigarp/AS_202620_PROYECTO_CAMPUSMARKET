import ast
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"
OWNERS = {"publicaciones": "publicaciones", "publicacion_imagenes": "publicaciones", "usuarios": "usuarios", "sesiones_usuario": "usuarios", "intentos_autenticacion": "usuarios", "reportes_publicacion": "administracion", "favoritos": "favoritos", "conversaciones": "mensajeria", "mensajes": "mensajeria"}
WRITE = re.compile(r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+([a-z_]+)\b", re.IGNORECASE)


def test_cada_tabla_solo_tiene_escritor_en_su_repository():
    violations = []
    for path in APP.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for table in WRITE.findall(node.value):
                    owner = OWNERS.get(table.lower())
                    if owner and path != APP / owner / "repository.py":
                        violations.append(str(path.relative_to(APP)))
    assert not violations


def test_ningun_contexto_importa_repository_ajeno_incluso_por_alias():
    violations = []
    for owner in ("usuarios", "publicaciones", "catalogo", "administracion", "favoritos", "mensajeria"):
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
