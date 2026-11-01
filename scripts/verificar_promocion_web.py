"""Lecturas de Compose/Git/registro; no crea, descarga imagenes ni despliega Docker."""

import argparse
import copy
import hashlib
import json
import os
import secrets
import subprocess
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "40be256f52d74ad8c9148886f040845658a38855"
SOURCE = "a9b6709a67f8036346acb64b9c2b9849ee355cf2"
DIGEST = "sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd"
IMAGE_ID = "sha256:15a6fee324bc315d27ab85674781dfd1bded727243cb6ff752370e70b5d6fd19"
IMAGE = "ghcr.io/nnigarp/campusmarket-web-candidate@" + DIGEST


def read_command(argv):
    return subprocess.run(argv, check=True, capture_output=True, text=True, cwd=ROOT).stdout


def config_delta():
    binary = os.environ.get("CM_COMPOSE_BINARY")
    compose = [binary] if binary else ["docker", "compose"]
    with tempfile.TemporaryDirectory(prefix="campusmarket-config-") as directory:
        envfile = Path(directory) / "synthetic.env"
        values = {"MYSQL_PASSWORD": secrets.token_hex(24), "MYSQL_ROOT_PASSWORD": secrets.token_hex(24),
                  "MYSQL_DATABASE": "campusmarket_configuration_test", "MYSQL_USER": "campusmarket_app",
                  "CAMPUSMARKET_ADMIN_USER_IDS": "3", "CAMPUSMARKET_CORS_ORIGINS": "https://campusmarket.iscoutb.dev"}
        envfile.write_text("\n".join(k + "=" + v for k, v in values.items()) + "\n")
        envfile.chmod(0o600)
        prefix = compose + ["--project-name", "campusmarket-config-test", "--env-file", str(envfile)]
        configs = [json.loads(read_command(prefix + ["-f", "deploy/compose." + name + ".yaml", "config", "--format", "json"]))
                   for name in ("lab", "prod")]
        before, after = configs
        expected = copy.deepcopy(before)
        assert "build" in expected["services"]["api"]
        expected["services"]["api"].pop("build")
        expected["services"]["api"]["image"] = IMAGE
        assert after == expected, "El cambio supera api.build -> api.image"
        assert set(after["services"]) == {"api", "db"}
        assert before["services"]["db"] == after["services"]["db"]
        assert all(not cfg.get("build") and not cfg.get("ports") for cfg in after["services"].values())
        assert before["networks"] == after["networks"] and before["volumes"] == after["volumes"]
        assert sum(int(cfg["deploy"]["resources"]["limits"]["memory"]) for cfg in after["services"].values()) == 512 * 1024**2
        assert (ROOT / "deploy/compose.prod.yaml").read_bytes() == read_command(["git", "show", BASE + ":deploy/compose.prod.yaml"]).replace(
            "ghcr.io/iscoutb/campusmarket-api@sha256:f9eaabdb166274225e9ad490c44999f71f6b1f7c9c5902dc68ab98b07115ce8b", IMAGE).encode()
    return {"only_delta": "api.build -> api.image", "db_unchanged": True, "environment_references_unchanged": True,
            "networks_volumes_services_unchanged": True, "containers": 2, "memory_limit_bytes": 512 * 1024**2}


def source_compatibility():
    def tree(ref):
        lines = read_command(["git", "ls-tree", "-r", ref, "--", "backend/app", "backend/requirements.txt", "contracts/openapi-v2.json"]).splitlines()
        return {line.split("\t", 1)[1]: line.split("\t", 1)[0] for line in lines
                if line.split("\t", 1)[1] not in {"backend/app/main.py", "backend/app/web_frontend.py"}}
    assert tree(BASE) == tree(SOURCE), "Cambios en persistencia/API distintos del montaje Web"
    return {"base": BASE, "image_source": SOURCE, "storage_domain_dependencies_contract_identical": True,
            "running_production_source_verified": False}


def registry_identity():
    package = "nnigarp/campusmarket-web-candidate"
    with urllib.request.urlopen("https://ghcr.io/token?service=ghcr.io&scope=repository:" + package + ":pull", timeout=30) as response:
        token = json.load(response)["token"]
    headers = {"Authorization": "Bearer " + token, "Accept": "application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json"}
    def read(path):
        req = urllib.request.Request("https://ghcr.io/v2/" + package + path, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    manifest_bytes = read("/manifests/" + DIGEST)
    assert "sha256:" + hashlib.sha256(manifest_bytes).hexdigest() == DIGEST
    manifest = json.loads(manifest_bytes)
    assert manifest["config"]["digest"] == IMAGE_ID
    config_bytes = read("/blobs/" + IMAGE_ID)
    assert "sha256:" + hashlib.sha256(config_bytes).hexdigest() == IMAGE_ID
    cfg = json.loads(config_bytes)
    assert cfg["os"] == "linux" and cfg["architecture"] == "amd64"
    assert cfg["config"]["Labels"]["org.opencontainers.image.revision"] == SOURCE
    assert cfg["config"]["User"] == "campusmarket"
    return {"manifest_digest": DIGEST, "image_id": IMAGE_ID, "oci_source": SOURCE,
            "anonymous_registry_read": True, "production_cache_verified": False, "rebuilt": False, "republished": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = {"compose": config_delta(), "compatibility": source_compatibility(), "production_deployed": False,
                  "production_recovery_verified": False}
        if args.registry:
            result["registry"] = registry_identity()
        result["passed"] = True
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result))
    except (AssertionError, OSError, ValueError, LookupError, subprocess.SubprocessError) as error:
        print("Validacion fallida: " + type(error).__name__ + "; salida privada omitida")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
