"""Verificacion de solo lectura del cambio de imagen API para CampusMarket.

No despliega ni descarga datos de produccion. Verifica el Compose normalizado con
credenciales sinteticas y que el unico delta es la referencia inmutable de API.
"""
import copy
import json
import secrets
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IMAGE = (
    "ghcr.io/nnigarp/campusmarket-web-universidades@"
    "sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1"
)
PREVIOUS_IMAGE = (
    "ghcr.io/nnigarp/campusmarket-web-candidate@"
    "sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd"
)

def command(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    from_git = command("git", "show", "HEAD^1:deploy/compose.prod.yaml")
    current = (ROOT / "deploy/compose.prod.yaml").read_text()
    assert from_git.count(PREVIOUS_IMAGE) == 1, "Imagen previa desconocida"
    assert current == from_git.replace(PREVIOUS_IMAGE, EXPECTED_IMAGE, 1), (
        "El unico cambio permitido es api.image por digest"
    )

    with tempfile.TemporaryDirectory(prefix="cm-promotion-") as tmp:
        envfile = Path(tmp) / "local.env"
        envfile.write_text("\n".join([
            "MYSQL_ROOT_PASSWORD=" + secrets.token_hex(20),
            "MYSQL_PASSWORD=" + secrets.token_hex(20),
            "MYSQL_DATABASE=campusmarket_compose_test",
            "MYSQL_USER=campusmarket_app",
        ]) + "\n")
        envfile.chmod(0o600)
        prefix = ["docker", "compose", "-p", "campusmarket-release-ci", "--env-file", str(envfile)]
        oldfile = Path(tmp) / "previous.yaml"
        oldfile.write_text(from_git)
        before = json.loads(command(*(prefix + ["-f", str(oldfile), "config", "--format", "json"])))
        after = json.loads(command(*(prefix + ["-f", "deploy/compose.prod.yaml", "config", "--format", "json"])))
        expected = copy.deepcopy(before)
        expected["services"]["api"]["image"] = EXPECTED_IMAGE
        assert after == expected, "Delta de Compose supera el cambio de api.image"
        assert set(after["services"]) == {"api", "db"}
        assert after["services"]["db"] == before["services"]["db"]
        assert after["networks"] == before["networks"]
        assert after["volumes"] == before["volumes"]
        assert all(not cfg.get("build") and not cfg.get("ports") for cfg in after["services"].values())
        limit = sum(int(cfg["deploy"]["resources"]["limits"]["memory"]) for cfg in after["services"].values())
        assert limit == 512 * 1024 * 1024
    result = {
        "passed": True, "change": "api.image only",
        "image": EXPECTED_IMAGE,
        "db_unchanged": True, "networks_unchanged": True,
        "volumes_unchanged": True, "container_count": 2,
        "production_deployed": False, "backup_recovery_verified": False,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
