"""Vincular manifiesto GHCR con Image ID ensayado, sin reconstruir."""

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "ghcr.io/nnigarp/campusmarket-web-universidades"


def command(args):
    return subprocess.check_output(args, text=True).strip()


def main():
    expected = json.loads((ROOT / "artifacts/incremento2-imagen/ensayo.json").read_text())
    if not expected.get("passed"):
        raise RuntimeError("El ensayo integral no está aprobado.")
    digest = os.environ["PUBLISHED_DIGEST"]
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
        raise ValueError("Digest publicado inválido.")
    reference = f"{PACKAGE}@{digest}"
    manifest = json.loads(command(["docker", "buildx", "imagetools", "inspect", "--raw", reference]))
    runtime_digest = digest
    if "manifests" in manifest:
        matches = [m for m in manifest["manifests"] if m.get("platform", {}).get("os") == "linux"
                   and m.get("platform", {}).get("architecture") == "amd64"]
        if len(matches) != 1:
            raise RuntimeError("No hay un manifiesto de runtime linux/amd64 único.")
        runtime_digest = matches[0]["digest"]
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", runtime_digest):
            raise ValueError("Digest de runtime inválido.")
        manifest = json.loads(command(["docker", "buildx", "imagetools", "inspect", "--raw", f"{PACKAGE}@{runtime_digest}"]))
    if manifest.get("config", {}).get("digest") != expected["image_id"]:
        raise RuntimeError("La configuración publicada no corresponde al Image ID ensayado.")
    command(["docker", "pull", reference])
    actual = json.loads(command(["docker", "image", "inspect", reference]))[0]
    if actual["Id"] != expected["image_id"] or actual["Config"]["Labels"]["org.opencontainers.image.revision"] != expected["source"]:
        raise RuntimeError("La descarga por digest no conserva identidad/fuente.")
    result = {"source_sha": expected["source"], "base_master": expected["base_master"],
              "image_id": actual["Id"], "image": reference, "runtime_manifest_digest": runtime_digest,
              "config_digest": manifest["config"]["digest"], "previous_image": expected["previous_image"],
              "contract_sha256": expected["contract_sha256"], "web_main_sha256": expected["web_main_sha256"],
              "run_id": os.environ["GITHUB_RUN_ID"], "production_changed": False,
              "registry_pull_verified_in_ci": True, "dokploy_pull_verified": False}
    (ROOT / "artifacts/incremento2-imagen/publicacion.json").write_text(json.dumps(result, indent=2) + "\n")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
        stream.write("```json\n" + json.dumps(result, indent=2) + "\n```\nPreparada y NO desplegada.\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
