"""Separar base oficial, candidato y contrato/revisión del despliegue S10.

Solo lee Git y escribe evidencia local. No obtiene el contrato esperado del
servidor bajo prueba y nunca interpreta el header de revisión como un Git ref.
"""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

OFFICIAL_REMOTE = "https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET.git"
CONTRACT = "contracts/openapi-v2.json"


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def sha(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("Se requiere un SHA completo de 40 caracteres hexadecimales.")
    return value


def contract_at(root: Path, revision: str) -> dict:
    data = json.loads(git(root, "show", f"{sha(revision)}:{CONTRACT}"))
    if not isinstance(data, dict) or not data.get("paths") or not data.get("openapi"):
        raise ValueError("La referencia no contiene un contrato OpenAPI válido.")
    return data


def prepare(root: Path, output: Path, *, upstream: str = OFFICIAL_REMOTE,
            mode: str = "produccion", expected_revision: str = "") -> dict:
    root = root.resolve()
    output.mkdir(parents=True, exist_ok=False)
    orchestration_sha = sha(git(root, "rev-parse", "HEAD"))
    candidate_sha = orchestration_sha
    # URL fija en CI. El parámetro permite repositorios Git sintéticos en tests.
    # FETCH_HEAD se captura inmediatamente; no se consulta HEAD^1 ni origin/master
    # (que en un fork no identifica necesariamente la base institucional).
    git(root, "fetch", "--no-tags", upstream, "refs/heads/master")
    base_sha = sha(git(root, "rev-parse", "FETCH_HEAD"))
    base = contract_at(root, base_sha)
    config = json.loads((root / ".github/s10-produccion.json").read_text(encoding="utf-8"))
    production_sha = sha(config["contract_commit"])
    runtime_revision = sha(config["runtime_revision"])
    # Referencia inmutable del contrato observado en producción, independiente
    # del master futuro y del identificador usado por el build de la imagen.
    git(root, "fetch", "--no-tags", upstream, production_sha)
    production = contract_at(root, production_sha)
    if mode == "instalado":
        # La imagen puede preceder al fix del propio workflow. Mantener el
        # orquestador corregido y leer el contrato de la fuente exacta instalada.
        candidate_sha = sha(expected_revision)
        git(root, "fetch", "--no-tags", upstream, candidate_sha)
        candidate = contract_at(root, candidate_sha)
        reference, runtime_revision, reference_sha = candidate, candidate_sha, candidate_sha
    elif mode == "produccion":
        candidate = contract_at(root, candidate_sha)
        reference, reference_sha = production, production_sha
    else:
        raise ValueError("Modo S10 desconocido.")
    contracts = {"base": base, "candidate": candidate, "production": production, "reference": reference}
    hashes = {}
    for name, value in contracts.items():
        content = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        (output / f"{name}-contract.json").write_text(content, encoding="utf-8")
        hashes[name] = hashlib.sha256(content.encode()).hexdigest()
    evidence = {
        "mode": mode, "official_remote": upstream, "official_master_sha": base_sha,
        "orchestration_sha": orchestration_sha, "candidate_sha": candidate_sha,
        "production_contract_sha": production_sha,
        "reference_contract_sha": reference_sha, "expected_runtime_revision": runtime_revision,
        "previous_image": config["image"], "contract_sha256": hashes,
    }
    (output / "references.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("produccion", "instalado"), default="produccion")
    parser.add_argument("--expected-revision", default="")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = prepare(root, args.output, mode=args.mode, expected_revision=args.expected_revision)
    print(json.dumps(result, indent=2))
    with (args.output / "outputs.txt").open("w", encoding="utf-8") as stream:
        stream.write(f"expected_revision={result['expected_runtime_revision']}\n")


if __name__ == "__main__":
    main()
