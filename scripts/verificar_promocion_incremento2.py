"""Preflight de solo lectura: delta api.image, procedencia Git e identidad GHCR."""

import argparse
import copy
import hashlib
import json
import os
import re
import secrets
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "1c07c2c3c2610455b1dc1c07b4ebc4c2ab362e24"
PACKAGE = "nnigarp/campusmarket-web-universidades"


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def verify(registry=False):
    metadata = json.loads((ROOT / "deploy/promocion-incremento2.json").read_text())
    source = metadata["source_sha"]
    assert re.fullmatch(r"[0-9a-f]{40}", source)
    assert metadata["base_master"] == BASE
    assert metadata["config_digest"] == metadata["image_id"]
    assert metadata["registry_pull_verified_in_ci"] and not metadata["production_changed"]
    before_text = command(["git", "show", BASE + ":deploy/compose.prod.yaml"]) + "\n"
    current = (ROOT / "deploy/compose.prod.yaml").read_text()
    assert before_text.count(metadata["previous_image"]) == 1
    assert current == before_text.replace(metadata["previous_image"], metadata["image"], 1), "Delta mayor que api.image"
    assert metadata["image"].startswith("ghcr.io/" + PACKAGE + "@")
    digest = metadata["image"].split("@", 1)[1]
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
    binary = os.getenv("CM_COMPOSE_BINARY")
    compose = [binary] if binary else ["docker", "compose"]
    with tempfile.TemporaryDirectory(prefix="cm-i2-config-") as directory:
        directory = Path(directory)
        env = directory / "synthetic.env"
        env.write_text("MYSQL_ROOT_PASSWORD=" + secrets.token_hex(24) + "\nMYSQL_PASSWORD=" + secrets.token_hex(24)
                       + "\nMYSQL_DATABASE=campusmarket_configuration_test\nMYSQL_USER=campusmarket_app\n")
        env.chmod(0o600)
        previous = directory / "previous.yaml"
        previous.write_text(before_text)
        prefix = compose + ["-p", "campusmarket-i2-config", "--env-file", str(env)]
        before, after = [json.loads(command(prefix + ["-f", str(path), "config", "--format", "json"]))
                         for path in (previous, ROOT / "deploy/compose.prod.yaml")]
        expected = copy.deepcopy(before)
        expected["services"]["api"]["image"] = metadata["image"]
        assert after == expected, "Compose normalizado cambió servicios/Environment/red/volúmenes/límites"
        assert set(after["services"]) == {"api", "db"}
        assert after["services"]["db"]["image"] == "mysql:8.4"
        assert all(not s.get("ports") and not s.get("build") for s in after["services"].values())
        assert sum(int(s["deploy"]["resources"]["limits"]["memory"]) for s in after["services"].values()) == 512 * 1024**2
    command(["git", "merge-base", "--is-ancestor", BASE, source])
    changed = command(["git", "diff", "--name-only", BASE, source, "--", "backend/app", "frontend", "contracts"]).splitlines()
    assert changed == ["backend/app/web_entrypoint.py"], "Código de imagen distinto al incremento integrado"
    contract = json.loads(command(["git", "show", source + ":contracts/openapi-v2.json"]))
    assert hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest() == metadata["contract_sha256"]
    evidence = json.loads((ROOT / "docs/evidencias/datos/imagen-incremento2-41595618179.json").read_text())
    assert evidence["ensayo"]["passed"] and evidence["publicacion"] == metadata
    assert len({x["services"]["db"]["container_id"] for x in evidence["ensayo"]["resources"]}) == 1
    registry_result = {"verified": False}
    if registry:
        with urlopen("https://ghcr.io/token?service=ghcr.io&scope=repository:" + PACKAGE + ":pull", timeout=30) as response:
            token = json.load(response)["token"]
        headers = {"Authorization": "Bearer " + token,
                   "Accept": "application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.index.v1+json"}
        def read(path):
            with urlopen(Request("https://ghcr.io/v2/" + PACKAGE + path, headers=headers), timeout=30) as response:
                return response.read()
        raw = read("/manifests/" + digest)
        assert "sha256:" + hashlib.sha256(raw).hexdigest() == digest
        manifest = json.loads(raw)
        if "manifests" in manifest:
            runtime = metadata["runtime_manifest_digest"]
            assert any(m["digest"] == runtime and m.get("platform", {}).get("architecture") == "amd64" for m in manifest["manifests"])
            raw = read("/manifests/" + runtime)
            assert "sha256:" + hashlib.sha256(raw).hexdigest() == runtime
            manifest = json.loads(raw)
        assert manifest["config"]["digest"] == metadata["image_id"]
        config_bytes = read("/blobs/" + metadata["image_id"])
        assert "sha256:" + hashlib.sha256(config_bytes).hexdigest() == metadata["image_id"]
        config = json.loads(config_bytes)
        assert config["os"] == "linux" and config["architecture"] == "amd64"
        assert config["config"]["Labels"]["org.opencontainers.image.revision"] == source
        assert config["config"]["User"] == "campusmarket"
        registry_result = {"verified": True, "anonymous_read": True, "manifest_digest": digest,
                           "config_digest": metadata["image_id"], "oci_source": source}
    return {"passed": True, "image": metadata["image"], "previous_image": metadata["previous_image"],
            "source": source, "base": BASE, "only_delta": "api.image", "db_environment_network_volumes_limits_unchanged": True,
            "containers": 2, "memory_limit_bytes": 512 * 1024**2, "registry": registry_result,
            "production_changed": False, "dokploy_pull_verified": False, "productive_backup_restore_verified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.registry)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
