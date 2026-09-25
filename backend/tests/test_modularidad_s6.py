import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "backend" / "app"

PUBLICACIONES_REPOSITORY = (
    APP_DIR / "publicaciones" / "repository.py"
)

OTHER_CONTEXTS = (
    APP_DIR / "usuarios",
    APP_DIR / "catalogo",
    APP_DIR / "administracion",
)

WRITE_PUBLICACIONES_PATTERN = re.compile(
    r"\b(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+publicaciones\b",
    re.IGNORECASE,
)


def python_files(directory: Path):
    return directory.rglob("*.py") if directory.exists() else []


def test_publicaciones_tiene_un_unico_escritor_productivo():
    writers = []

    for file_path in APP_DIR.rglob("*.py"):
        content = file_path.read_text(encoding="utf-8")

        if WRITE_PUBLICACIONES_PATTERN.search(content):
            writers.append(
                file_path.relative_to(REPO_ROOT).as_posix()
            )

    assert writers == [
        "backend/app/publicaciones/repository.py"
    ]


def test_otros_contextos_no_acceden_directamente_a_persistencia():
    violations = []

    for context_dir in OTHER_CONTEXTS:
        for file_path in python_files(context_dir):
            content = file_path.read_text(
                encoding="utf-8"
            ).lower()

            if (
                "sqlite3" in content
                or "pymysql" in content
            ):
                violations.append(
                    file_path.relative_to(REPO_ROOT).as_posix()
                )

    assert violations == []


def test_otros_contextos_no_importan_repository_de_publicaciones():
    violations = []

    forbidden_patterns = (
        "backend.app.publicaciones.repository",
        "publicaciones.repository",
    )

    for context_dir in OTHER_CONTEXTS:
        for file_path in python_files(context_dir):
            content = file_path.read_text(
                encoding="utf-8"
            )

            if any(
                pattern in content
                for pattern in forbidden_patterns
            ):
                violations.append(
                    file_path.relative_to(REPO_ROOT).as_posix()
                )

    assert violations == []


def test_flujo_publicaciones_respeta_router_service_repository():
    router = (
        APP_DIR / "publicaciones" / "router.py"
    ).read_text(encoding="utf-8")

    service = (
        APP_DIR / "publicaciones" / "service.py"
    ).read_text(encoding="utf-8")

    repository = PUBLICACIONES_REPOSITORY.read_text(
        encoding="utf-8"
    )

    assert "from .service import" in router
    assert "from .repository import" in service

    assert "sqlite3" not in router
    assert "sqlite3" not in service
    assert "sqlite3" not in repository

    assert "pymysql" not in router
    assert "pymysql" not in service
    assert "pymysql" in repository


def test_repositorio_publicaciones_contiene_la_persistencia_del_contexto():
    content = PUBLICACIONES_REPOSITORY.read_text(
        encoding="utf-8"
    )

    assert "CREATE TABLE IF NOT EXISTS publicaciones" in content
    assert "INSERT INTO publicaciones" in content
    assert "FROM publicaciones" in content