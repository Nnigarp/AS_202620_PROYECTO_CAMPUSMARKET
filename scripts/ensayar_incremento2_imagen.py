"""Ensayo único de imagen: migración, persistencia y rollback solo en Docker de CI."""

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "1c07c2c3c2610455b1dc1c07b4ebc4c2ab362e24"
PREVIOUS = "ghcr.io/nnigarp/campusmarket-web-universidades@sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1"
PREVIOUS_REVISION = "50d9352e5081f8c3e470bd9cda9220d21b14cc0a"
STATE = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "cm-i2-private-state.json"
OUT = ROOT / "artifacts/incremento2-imagen"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def guard() -> str:
    require(os.getenv("GITHUB_ACTIONS") == "true", "Solo se admite el runner efímero GitHub Actions.")
    run, attempt = os.getenv("GITHUB_RUN_ID", ""), os.getenv("GITHUB_RUN_ATTEMPT", "")
    require(run.isdigit() and attempt.isdigit(), "Identidad de runner inválida.")
    return f"cm-i2-{run}-{attempt}"


def command(args, *, stdin=None, env=None):
    result = subprocess.run(args, input=stdin, text=True, capture_output=True, env=env, check=False)
    if result.returncode:
        # Nunca registrar argumentos/inspect/config, pues pueden contener Environment.
        raise RuntimeError(f"Comando del ensayo falló (exit {result.returncode}).")
    return result.stdout.strip()


def save(state):
    descriptor = os.open(STATE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(state, stream)


def load():
    state = json.loads(STATE.read_text())
    require(state["project"] == guard(), "Estado de otro proyecto: operación rechazada.")
    return state


def compose(state, *args, image=None):
    env = {**os.environ, "API_IMAGE": image or state["candidate"]}
    return command(["docker", "compose", "-p", state["project"], "-f", state["compose"], *args], env=env)


def image_data(image):
    value = json.loads(command(["docker", "image", "inspect", image]))[0]
    return {"id": value["Id"], "revision": value["Config"]["Labels"].get("org.opencontainers.image.revision")}


def prepare():
    project = guard()
    require(not STATE.exists(), "Ya existe estado privado; no sobrescribir otro ensayo.")
    source = command(["git", "rev-parse", "HEAD"])
    require(re.fullmatch(r"[0-9a-f]{40}", source), "SHA de fuente inválido.")
    require(source == os.environ.get("GITHUB_SHA"), "Checkout distinto al run.")
    command(["git", "merge-base", "--is-ancestor", BASE_SHA, source])
    changed = command(["git", "diff", "--name-only", BASE_SHA, source, "--", "backend/app", "frontend", "contracts"]).splitlines()
    require(changed == ["backend/app/web_entrypoint.py"], "El empaquetado cambió código funcional ya aprobado.")
    require(not command(["docker", "ps", "-aq", "--filter", f"label=com.docker.compose.project={project}"]), "Proyecto ya ocupado.")
    private = Path(tempfile.mkdtemp(prefix=project + "-", dir=os.environ["RUNNER_TEMP"]))
    env_file = private / "synthetic.env"
    values = {"MYSQL_ROOT_PASSWORD": secrets.token_hex(24), "MYSQL_PASSWORD": secrets.token_hex(24),
              "MYSQL_USER": "campusmarket_app", "MYSQL_DATABASE": "campusmarket_i2_test", "CAMPUSMARKET_ADMIN_USER_IDS": "3"}
    env_file.write_text("\n".join(f"{k}={v}" for k, v in values.items()) + "\n")
    env_file.chmod(0o600)
    rendered = json.loads(command(["docker", "compose", "-p", project, "--env-file", str(env_file),
                                   "-f", str(ROOT / "deploy/compose.prod.yaml"), "config", "--format", "json"]))
    require(set(rendered["services"]) == {"api", "db"}, "Solo api/db.")
    require(set(rendered["volumes"]) == {"mysql_data", "publication_images"}, "Volúmenes distintos al esquema productivo.")
    require(rendered["services"]["db"]["image"] == "mysql:8.4", "Versión MySQL alterada.")
    for service in rendered["services"].values():
        require(not service.get("ports") and not service.get("build") and not service.get("privileged"), "Puertos/build/privilegios inesperados.")
        require(all(m["type"] == "volume" for m in service.get("volumes", [])), "Montaje no permitido.")
    for volume in rendered["volumes"].values():
        require(not volume.get("external") and volume["name"].startswith(project + "_"), "Volumen externo no permitido.")
    require(len(rendered["networks"]) == 1 and "default" in rendered["networks"], "Solo una red efímera.")
    rendered["networks"]["default"]["internal"] = True
    require(rendered["networks"]["default"]["name"] == project + "_default", "Red ajena al proyecto.")
    candidate = "campusmarket-i2-local:" + source
    rendered["services"]["api"]["image"] = "${API_IMAGE}"
    path = private / "compose.json"
    path.write_text(json.dumps(rendered))
    path.chmod(0o600)
    contract = json.loads((ROOT / "contracts/openapi-v2.json").read_text())
    state = {"project": project, "compose": str(path), "candidate": candidate, "source": source,
             "http": {"project": project, "candidate_contract_sha256": hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest(),
                      "candidate_web_main_sha256": hashlib.sha256((ROOT / "frontend/campusmarket/build/web/main.dart.js").read_bytes()).hexdigest()},
             "checks": [], "resources": []}
    save(state)
    compose(state, "config", "--quiet")
    candidate_data = image_data(candidate)
    require(candidate_data["revision"] == source, "Label de candidato incorrecta.")
    require(command(["docker", "run", "--rm", "--network", "none", "--entrypoint", "cat", candidate, "/app/REVISION"]) == source,
            "REVISION distinta al código construido.")
    state["image_id"] = candidate_data["id"]
    command(["docker", "pull", PREVIOUS])
    state["previous_image_id"] = image_data(PREVIOUS)["id"]
    require(image_data(PREVIOUS)["revision"] == PREVIOUS_REVISION, "Imagen previa no corresponde al rollback declarado.")
    save(state)


def snapshot(state, label, expected_image_id):
    ids = compose(state, "ps", "-q").splitlines()
    require(len(ids) == 2, "Número de contenedores distinto a dos.")
    services = {}
    for id_ in ids:
        value = json.loads(command(["docker", "inspect", id_]))[0]
        require(value["Config"]["Labels"]["com.docker.compose.project"] == state["project"], "Contenedor ajeno.")
        name = value["Config"]["Labels"]["com.docker.compose.service"]
        require(value["State"]["Health"]["Status"] == "healthy" and not value["State"]["OOMKilled"], "Servicio no saludable/OOM.")
        require(value["HostConfig"]["Memory"] == 256 * 1024**2, "Límite de 256 MiB no aplicado.")
        require(len(value["NetworkSettings"]["Networks"]) == 1, "Red adicional en ensayo.")
        peak = int(command(["docker", "exec", id_, "cat", "/sys/fs/cgroup/memory.peak"]))
        services[name] = {"container_id": value["Id"], "image_id": value["Image"], "memory_limit": value["HostConfig"]["Memory"],
                          "memory_peak": peak, "mounts": [{"name": m["Name"], "destination": m["Destination"]} for m in value["Mounts"]]}
    require(services["api"]["image_id"] == expected_image_id, "API ejecutó otra imagen.")
    if "db_container_id" not in state:
        state["db_container_id"] = services["db"]["container_id"]
    require(services["db"]["container_id"] == state["db_container_id"], "MySQL fue recreado durante promoción/rollback.")
    state["resources"].append({"phase": label, "services": services})


def http(state, phase, revision):
    script = (ROOT / "scripts/ensayar_incremento2_http.py").read_text()
    args = ["docker", "compose", "-p", state["project"], "-f", state["compose"], "exec", "-T", "api", "python", "-c", script]
    result = subprocess.run(args, input=json.dumps({"phase": phase, "state": state["http"], "revision": revision}),
                            text=True, capture_output=True, check=False, env={**os.environ, "API_IMAGE": state["candidate"]})
    try:
        data = json.loads(result.stdout)
    except ValueError:
        raise RuntimeError("Cliente HTTP no produjo evidencia válida.") from None
    if result.returncode:
        raise RuntimeError(f"Fase HTTP {phase}: {data.get('error', 'error')} — {data.get('detail', 'sin detalle seguro')}")
    state["http"] = data["state"]
    state["checks"].extend(f"{phase}:{item}" for item in data["checks"])
    save(state)


def run():
    state = load()
    compose(state, "up", "-d", "--no-build", "--wait", "--wait-timeout", "180", image=PREVIOUS)
    snapshot(state, "previous", state["previous_image_id"])
    http(state, "seed", PREVIOUS_REVISION)
    compose(state, "up", "-d", "--no-deps", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180", "api")
    snapshot(state, "candidate", state["image_id"])
    http(state, "upgrade", state["source"])
    compose(state, "restart", "api")
    compose(state, "up", "-d", "--no-deps", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180", "api")
    http(state, "persist", state["source"])
    snapshot(state, "restart", state["image_id"])
    compose(state, "up", "-d", "--no-deps", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180", "api", image=PREVIOUS)
    http(state, "rollback", PREVIOUS_REVISION)
    snapshot(state, "rollback", state["previous_image_id"])
    compose(state, "up", "-d", "--no-deps", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180", "api")
    http(state, "persist", state["source"])
    snapshot(state, "restore-candidate", state["image_id"])
    require(image_data(state["candidate"])["id"] == state["image_id"], "Se reconstruyó la imagen ensayada.")
    state["passed"] = True
    save(state)


def report():
    state = load()
    OUT.mkdir(parents=True, exist_ok=True)
    public = {k: state[k] for k in ("project", "source", "image_id", "previous_image_id", "checks", "resources", "passed") if k in state}
    public.update({"base_master": BASE_SHA, "previous_image": PREVIOUS, "production_changed": False})
    public.update({"contract_sha256": state["http"]["candidate_contract_sha256"],
                   "web_main_sha256": state["http"]["candidate_web_main_sha256"],
                   "packaging_reused_from": PREVIOUS_REVISION,
                   "reused_code_ci": [41591551904, 41591551934, 41591551894, 41591551878],
                   "s10_correction_ci": 41595145649})
    (OUT / "ensayo.json").write_text(json.dumps(public, indent=2) + "\n")
    print(json.dumps({"passed": state.get("passed", False), "checks": len(state["checks"]), "source": state["source"]}))


def cleanup():
    guard()
    if not STATE.exists():
        return
    state = load()
    # Compose generado solo contiene recursos con el prefijo único del run.
    compose(state, "down", "--volumes", "--remove-orphans")
    require(not command(["docker", "ps", "-aq", "--filter", f'label=com.docker.compose.project={state["project"]}']), "Quedaron contenedores del ensayo.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "report", "cleanup"))
    action = parser.parse_args().action
    globals()[action]()
