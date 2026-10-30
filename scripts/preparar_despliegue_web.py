"""Preflight de solo lectura y plan de API; no ejecuta up, pull, exec ni restauraciones.

El operador debe aportar evidencias externas: el programa no puede certificar
autodeploy, autorización ni recuperabilidad a partir de Docker inspect.
Nunca se archivan config/inspect completos ni Environment.
"""

import argparse
import copy
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "ghcr.io/nnigarp/campusmarket-web-candidate@sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd"
IMAGE_ID = "sha256:15a6fee324bc315d27ab85674781dfd1bded727243cb6ff752370e70b5d6fd19"
SOURCE = "a9b6709a67f8036346acb64b9c2b9849ee355cf2"
PROJECT = "campusmarket-sistema-2zvsxj"
OVERLAY = ROOT / "deploy/compose.web.yaml"
GATES = (
    "authorization", "autodeploy_paused", "no_queued_deployments",
    "consistent_backup_restored", "rollback_archive_restored",
    "schema_compatible", "ghcr_pull_from_server",
)
UP_API = ["up", "-d", "--no-deps", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180", "api"]


class Blocked(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Blocked(message)


def command(parts):
    try:
        result = subprocess.run(parts, capture_output=True, text=True, timeout=90, check=False)
    except (OSError, subprocess.SubprocessError):
        raise Blocked("Comando de lectura no disponible; salida privada omitida") from None
    require(result.returncode == 0, "Falló una lectura Docker/Compose; salida privada omitida")
    return result.stdout


def validate_delta(before, after):
    """Solo api.build -> api.image; también preserva overrides de Dokploy."""
    normalized = copy.deepcopy(before)
    require(set(before.get("services", {})) == {"api", "db"}, "Se requieren solo api y db")
    normalized["services"]["api"].pop("build", None)
    normalized["services"]["api"]["image"] = IMAGE
    require(after == normalized, "El cambio altera algo distinto de la imagen/build de API")
    require(not any(service.get("build") for service in after["services"].values()), "El plan contiene un build")
    for service in after["services"].values():
        limits = service.get("deploy", {}).get("resources", {}).get("limits", {})
        require(limits.get("memory") == "268435456" and str(limits.get("cpus")) == "0.5", "Límites distintos de 256 MiB/0,5 CPU")
        require(not service.get("privileged") and not service.get("container_name"), "Configuración no admitida")


def validate_attestations(data, project, now=None):
    now = now or datetime.now(timezone.utc)
    checked = datetime.fromisoformat(data["checked_at"])
    require(checked.tzinfo is not None and 0 <= (now - checked).total_seconds() <= 1800, "Preflight sin fecha reciente (máximo 30 minutos)")
    scope = data.get("scope")
    if scope == "synthetic-ci":
        require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted", "Scope sintético solo en runner efímero")
        expected = "campusmarket-ghcr-" + os.environ.get("GITHUB_RUN_ID", "") + "-" + os.environ.get("GITHUB_RUN_ATTEMPT", "")
        require(project == expected, "Proyecto sintético distinto del run")
    else:
        require(scope == "production" and project == PROJECT, "Proyecto productivo inesperado")
    require(data.get("project") == project, "Evidencia de otro proyecto")
    for gate in GATES:
        item = data.get("gates", {}).get(gate, {})
        require(item.get("verified") is True and bool(str(item.get("evidence", "")).strip()), "BLOQUEADO: " + gate)
    rollback = data.get("rollback", {})
    require(re.fullmatch(r"sha256:[0-9a-f]{64}", rollback.get("image_id", "")), "Falta Image ID anterior")
    require(re.fullmatch(r"[0-9a-f]{64}", rollback.get("archive_sha256", "")), "Falta checksum del respaldo de imagen anterior")


def validate_image(image):
    require(image["Id"] == IMAGE_ID and IMAGE in image.get("RepoDigests", []), "Digest/Image ID distinto de la imagen aprobada")
    require(image["Os"] == "linux" and image["Architecture"] == "amd64", "Plataforma inesperada")
    require(image["Config"].get("Labels", {}).get("org.opencontainers.image.revision") == SOURCE, "OCI distinta de la fuente aprobada")


def snapshot(config, inspect_service):
    """Contrasta montajes físicos y configuración efectiva sin leer SQL/archivos."""
    result = {}
    for service in ("api", "db"):
        cfg = config["services"][service]
        data = inspect_service(service)
        labels = data["Config"]["Labels"]
        require(labels.get("com.docker.compose.project") == config["name"] and labels.get("com.docker.compose.service") == service, "Contenedor ajeno al proyecto/servicio")
        require(data["State"].get("Running") and data["State"].get("Health", {}).get("Status") == "healthy", "Servicio no healthy: " + service)
        require(not data["State"].get("OOMKilled") and data["RestartCount"] == 0, "OOM/reinicio sin resolver: " + service)
        require(data["HostConfig"]["Memory"] == 268435456 and data["HostConfig"]["NanoCpus"] == 500000000, "Cuotas efectivas distintas: " + service)
        env = dict(item.split("=", 1) for item in data["Config"].get("Env", []))
        require(all(env.get(k) == str(v) for k, v in cfg.get("environment", {}).items()), "Environment efectivo distinto: " + service)
        actual_labels = {k: v for k, v in labels.items() if not k.startswith("com.docker.compose.") and k in cfg.get("labels", {})}
        require(actual_labels == cfg.get("labels", {}), "Labels de routing/configuración distintas: " + service)
        # Si Dokploy inyectó labels que no figuran en los archivos aportados, bloquear.
        require(all(k in cfg.get("labels", {}) for k in labels if k.startswith("traefik.")), "Falta el Compose efectivo con routing de Dokploy")
        expected_mounts = []
        for mount in cfg.get("volumes", []):
            require(mount["type"] == "volume", "Solo volúmenes con nombre")
            volume = config["volumes"][mount["source"]]["name"]
            expected_mounts.append({"type": "volume", "name": volume, "target": mount["target"], "rw": not mount.get("read_only", False)})
        actual_mounts = [{"type": m["Type"], "name": m.get("Name"), "target": m["Destination"], "rw": m["RW"]} for m in data["Mounts"]]
        require(sorted(expected_mounts, key=lambda m: m["target"]) == sorted(actual_mounts, key=lambda m: m["target"]), "Montajes físicos distintos: " + service)
        networks = sorted(config["networks"][name]["name"] for name in cfg.get("networks", {}))
        require(networks == sorted(data["NetworkSettings"]["Networks"]), "Red efectiva distinta: " + service)
        result[service] = {"container_id": data["Id"], "image_id": data["Image"], "mounts": actual_mounts,
                           "networks": networks, "started_at": data["State"]["StartedAt"]}
    return result


def inspect_services(prefix, config):
    def inspect(service):
        cid = command(prefix + ["ps", "-aq", service]).strip()
        require(bool(re.fullmatch(r"[0-9a-f]{12,64}", cid)), "Falta un contenedor único: " + service)
        return json.loads(command(["docker", "inspect", cid]))[0]
    return snapshot(config, inspect)


def private_json(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def prepare(prefix, evidence, out):
    before = json.loads(command(prefix + ["config", "--format", "json"]))
    candidate = prefix + ["-f", str(OVERLAY)]
    after = json.loads(command(candidate + ["config", "--format", "json"]))
    validate_delta(before, after)
    validate_attestations(evidence, before["name"])
    validate_image(json.loads(command(["docker", "image", "inspect", IMAGE]))[0])
    baseline = inspect_services(prefix, before)
    previous = baseline["api"]["image_id"]
    require(previous == evidence["rollback"]["image_id"], "La copia recuperable no corresponde a la API activa")
    require(json.loads(command(["docker", "image", "inspect", previous]))[0]["Id"] == previous, "Imagen anterior no disponible localmente")
    require(not out.exists(), "No sobrescribir un plan anterior")
    out.mkdir(mode=0o700, parents=True)
    rollback_file = out / "rollback.compose.json"
    private_json(rollback_file, {"services": {"api": {"image": previous}}})
    rollback = candidate + ["-f", str(rollback_file)]
    rollback_config = json.loads(command(rollback + ["config", "--format", "json"]))
    expected = copy.deepcopy(after)
    expected["services"]["api"]["image"] = previous
    require(rollback_config == expected, "El rollback altera algo distinto de api.image")
    plan = {"project": before["name"], "scope": evidence["scope"], "checked_at": evidence["checked_at"],
            "candidate": IMAGE, "candidate_image_id": IMAGE_ID, "source_sha": SOURCE,
            "baseline": baseline, "rollback_image_id": previous, "compose_prefix": candidate,
            "promote": candidate + UP_API, "rollback": rollback + UP_API,
            "external_evidence": evidence, "executed": False}
    private_json(out / "plan.json", plan)
    return plan


def verify(plan, mode):
    prefix = plan["compose_prefix"]
    if mode == "rollback":
        # El prefijo del comando termina antes de la suborden up.
        prefix = plan["rollback"][:-len(UP_API)]
    config = json.loads(command(prefix + ["config", "--format", "json"]))
    current = inspect_services(prefix, config)
    require(current["db"] == plan["baseline"]["db"], "MySQL cambió: detener la publicación")
    for key in ("mounts", "networks"):
        require(current["api"][key] == plan["baseline"]["api"][key], "Cambió la persistencia/red de API")
    expected = IMAGE_ID if mode == "promoted" else plan["rollback_image_id"]
    require(current["api"]["image_id"] == expected, "API no ejecuta el Image ID esperado")
    return current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    create = sub.add_parser("prepare")
    create.add_argument("--project", required=True)
    create.add_argument("--env-file", type=Path, required=True)
    create.add_argument("--file", type=Path, action="append", required=True, help="Todos los Compose efectivos, en su orden original")
    create.add_argument("--evidence", type=Path, required=True)
    create.add_argument("--out", type=Path, required=True)
    check = sub.add_parser("verify")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--mode", choices=("promoted", "rollback"), required=True)
    args = parser.parse_args()
    try:
        if args.operation == "prepare":
            prefix = ["docker", "compose", "--project-name", args.project, "--env-file", str(args.env_file.resolve())]
            for file in args.file:
                prefix += ["-f", str(file.resolve())]
            prepare(prefix, json.loads(args.evidence.read_text()), args.out.resolve())
            print("Preflight completo; plan privado generado. Ningún despliegue ejecutado.")
        else:
            verify(json.loads(args.plan.read_text()), args.mode)
            print("Identidad, salud, MySQL, montajes y redes verificados; faltan las comprobaciones públicas.")
    except (Blocked, OSError, ValueError, LookupError, TypeError) as error:
        print(str(error) if isinstance(error, Blocked) else "Preflight incompleto o evidencia inválida; detalles privados omitidos")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
