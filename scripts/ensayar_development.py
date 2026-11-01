"""Ensaya SOLO el Compose development en un runner GitHub alojado y efimero.

No construye imagenes, no publica y no acepta proyectos, hosts ni credenciales
productivos. Reutiliza probes sinteticos aprobados; verifica la nueva topologia,
persistencia, dependencia y vuelta de una API fallida a la misma imagen aprobada.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import time
from pathlib import Path

from scripts.ensayar_imagen_ghcr import Trial, TrialError, require
from scripts.preparar_despliegue_web import (
    IMAGE,
    IMAGE_ID,
    ROOT,
    SOURCE,
    validate_image,
)

FORK = "Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET"
COMPOSE = ROOT / "deploy/compose.development.yaml"
DATABASE = "campusmarket_development_test"
MYSQL_IMAGE = "mysql:8.4@sha256:a0225d1ea6631c8bc2385dc4c2faba17bbf1834ecf369e1659a9a382bd8d5dd7"
MEMORY = 256 * 1024 * 1024
VOLUMES = {"api": ("dev_publication_images", "/app/backend/uploads"), "db": ("dev_mysql_data", "/var/lib/mysql")}
CHECKS = ("compose", "identity", "isolation", "web_origin", "persistence", "dependency", "rollback_panel", "memory", "cleanup")
MARKER = r'''
import hashlib,json,sys
from pathlib import Path
from backend.app.db import transaction
data=json.load(sys.stdin)
with transaction() as cursor:
    if data["create"]:
        cursor.execute("CREATE TABLE development_isolation_probe (marker VARCHAR(64) PRIMARY KEY)")
        cursor.execute("INSERT INTO development_isolation_probe VALUES (%s)",(data["marker"],))
    cursor.execute("SELECT marker FROM development_isolation_probe")
    assert cursor.fetchall()==[{"marker":data["marker"]}]
p=Path("/app/backend/uploads/development-isolation-probe.txt")
if data["create"]:
    p.write_text(data["marker"])
assert p.read_text()==data["marker"]
print(json.dumps({"sql_marker_matches":True,"upload_sha256":hashlib.sha256(p.read_bytes()).hexdigest()}))
'''
WEB = r'''
import json,urllib.request
origin="https://dev-campusmarket.iscoutb.dev"
with urllib.request.urlopen("http://127.0.0.1:8000/app/",timeout=5) as r:
    assert r.status==200 and b'<base href="/app/">' in r.read()
req=urllib.request.Request("http://127.0.0.1:8000/catalogo",method="OPTIONS",headers={
    "Origin":origin,"Access-Control-Request-Method":"GET","Access-Control-Request-Headers":"content-type"})
with urllib.request.urlopen(req,timeout=5) as r:
    assert r.status==200 and r.headers["Access-Control-Allow-Origin"]==origin
print(json.dumps({"app_status":200,"base_href":"/app/","development_cors":True,"public_https_verified":False}))
'''


def project_name(env, control=False):
    require(env.get("GITHUB_REPOSITORY") == FORK, "Este ensayo solo puede ejecutarse en el fork")
    require(env.get("GITHUB_ACTIONS") == "true" and env.get("RUNNER_ENVIRONMENT") == "github-hosted", "Solo runner GitHub alojado")
    require(env.get("GITHUB_SERVER_URL") == "https://github.com", "Servidor inesperado")
    require(not env.get("DOCKER_HOST") and env.get("DOCKER_CONTEXT", "default") in {"", "default"}, "Docker remoto no permitido")
    require(all(re.fullmatch(r"[0-9]+", env.get(k, "")) for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")), "Run invalido")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", env.get("GITHUB_SHA", ""))), "SHA invalido")
    return "campusmarket-development-" + env["GITHUB_RUN_ID"] + "-" + env["GITHUB_RUN_ATTEMPT"] + ("-control" if control else "")


def validate_config(config, project):
    require(bool(re.fullmatch(r"campusmarket-development-[0-9]+-[0-9]+(?:-control)?", project)), "Proyecto fuera del ensayo development")
    require(config.get("name") == project and set(config.get("services", {})) == {"api", "db"}, "Proyecto/servicios incorrectos")
    require(set(config.get("volumes", {})) == {v[0] for v in VOLUMES.values()}, "Volumenes no exclusivos de development")
    require(set(config.get("networks", {})) == {"default", "dev_data"}, "Redes inesperadas")
    require(not config.get("secrets") and not config.get("configs"), "No se admiten recursos externos")
    for key, network in config["networks"].items():
        require(network.get("name") == project + "_" + key and not network.get("external"), "Red global o externa")
        require(bool(network.get("internal")) == (key == "dev_data"), "Red de datos debe ser interna")
    for service, (volume, destination) in VOLUMES.items():
        cfg = config["services"][service]
        forbidden = ("build", "ports", "privileged", "cap_add", "container_name", "network_mode", "pid", "devices", "volumes_from", "external_links", "entrypoint")
        require(not any(cfg.get(k) for k in forbidden), "Opcion prohibida")
        require(set(cfg.get("networks", {})) == ({"default", "dev_data"} if service == "api" else {"dev_data"}), "Servicio en otra red")
        require(cfg.get("labels", {}).get("campusmarket.environment") == "development", "Falta etiqueta development")
        mounts = cfg.get("volumes", [])
        require(len(mounts) == 1 and mounts[0].get("type") == "volume" and mounts[0].get("source") == volume and mounts[0].get("target") == destination and not mounts[0].get("read_only"), "Montaje incorrecto")
        v = config["volumes"][volume]
        require(v.get("name") == project + "_" + volume and not v.get("external") and not v.get("driver_opts"), "Volumen global, externo o bind")
        require(cfg.get("healthcheck", {}).get("test"), "Falta healthcheck")
        limits = cfg.get("deploy", {}).get("resources", {}).get("limits", {})
        require(limits.get("cpus") in ("0.5", 0.5) and str(limits.get("memory")) == str(MEMORY), "Limites inesperados")
    api, db = (config["services"][s] for s in ("api", "db"))
    require(api.get("image") == IMAGE and db.get("image") == MYSQL_IMAGE, "Imagen incorrecta")
    a, d = api["environment"], db["environment"]
    require(a["CAMPUSMARKET_DB_HOST"] == "db" and a["CAMPUSMARKET_DB_NAME"] == d["MYSQL_DATABASE"] == DATABASE, "Base no sintetica")
    require(a["CAMPUSMARKET_DB_USER"] == d["MYSQL_USER"] == "campusmarket_dev", "Usuario no exclusivo")
    require(a["CAMPUSMARKET_DB_PASSWORD"] == d["MYSQL_PASSWORD"] and d["MYSQL_PASSWORD"] and d["MYSQL_ROOT_PASSWORD"] != d["MYSQL_PASSWORD"], "Claves incompletas o iguales")
    require(a["CAMPUSMARKET_CORS_ORIGINS"] == "https://dev-campusmarket.iscoutb.dev" and a["CAMPUSMARKET_ADMIN_USER_IDS"] == "", "Origen/admin inesperado")


class DevelopmentTrial(Trial):
    def __init__(self, control=False):
        self.project = project_name(os.environ, control)
        self.database = DATABASE
        self.private = Path(os.environ["RUNNER_TEMP"]) / self.project
        require(self.private.is_absolute(), "RUNNER_TEMP debe ser absoluto")
        self.env_file, self.state_file = self.private / "compose.env", self.private / "state.json"
        self.state = json.loads(self.state_file.read_text()) if self.state_file.exists() else {
            "project": self.project, "workflow_commit": os.environ["GITHUB_SHA"], "source_commit": SOURCE,
            "image": IMAGE, "image_id": IMAGE_ID, "checks": {},
            "run": "https://github.com/" + FORK + "/actions/runs/" + os.environ["GITHUB_RUN_ID"],
        }
        require(self.state["project"] == self.project and self.state["workflow_commit"] == os.environ["GITHUB_SHA"], "Estado de otro run")
        self.compose = ["docker", "compose", "--project-name", self.project, "--env-file", str(self.env_file), "-f", str(COMPOSE)]

    def config(self):
        cfg = json.loads(self.command(self.compose + ["config", "--format", "json"], "Compose development"))
        validate_config(cfg, self.project)
        return cfg

    def prepare_one(self):
        self.local_docker()
        require(not self.private.exists() and not any(self.inventory().values()), "Ya existen recursos del ensayo")
        self.save()
        values = {"DEV_MYSQL_ROOT_PASSWORD": secrets.token_hex(24), "DEV_MYSQL_PASSWORD": secrets.token_hex(24)}
        for value in values.values():
            print("::add-mask::" + value)
        fd = os.open(self.env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write("\n".join(k + "=" + v for k, v in values.items()) + "\n")
        self.config()
        self.state.update(prepared=True, marker=secrets.token_hex(16), compose_sha256=hashlib.sha256(COMPOSE.read_bytes()).hexdigest())
        self.save()

    def prepare(self):
        self.prepare_one()
        DevelopmentTrial(control=True).prepare_one()
        self.checked("compose", "Dos proyectos sinteticos, claves distintas, sin build, redes/volumenes propios")

    def marker(self, create=False):
        return json.loads(self.command(self.compose + ["exec", "-T", "api", "python", "-c", MARKER], "marcador sintetico", stdin=json.dumps({"create": create, "marker": self.state["marker"]})))

    def snapshot(self, phase):
        result = {}
        for service, (volume, target) in VOLUMES.items():
            data = self.inspect(service)
            require(data["State"]["Running"] and data["State"]["Health"]["Status"] == "healthy" and not data["State"]["OOMKilled"] and data["RestartCount"] == 0, "Contenedor no saludable")
            require(data["HostConfig"]["Memory"] == MEMORY and data["HostConfig"]["NanoCpus"] == 500_000_000, "Limites no aplicados")
            require(not any(data["HostConfig"].get(k) for k in ("PortBindings", "Privileged")), "Puertos/privilegios inesperados")
            mounts = [{"type": m["Type"], "name": m.get("Name"), "target": m["Destination"], "rw": m["RW"]} for m in data["Mounts"]]
            require(mounts == [{"type": "volume", "name": self.project + "_" + volume, "target": target, "rw": True}], "Montaje efectivo incorrecto")
            networks = set(data["NetworkSettings"]["Networks"])
            require(networks == {self.project + "_" + n for n in ({"default", "dev_data"} if service == "api" else {"dev_data"})}, "Red efectiva incorrecta")
            if service == "api":
                require(data["Image"] == IMAGE_ID and data["Config"]["Image"] == IMAGE, "Imagen de API distinta")
            else:
                require(data["Config"]["Image"] == MYSQL_IMAGE, "MySQL no esta fijado por digest")
            peak = int(self.command(self.compose + ["exec", "-T", service, "cat", "/sys/fs/cgroup/memory.peak"], "pico de memoria").strip())
            require(0 < peak <= MEMORY, "Pico fuera del limite")
            result[service] = {"container_id": data["Id"], "started_at": data["State"]["StartedAt"], "restart_count": data["RestartCount"],
                               "image_id": data["Image"], "memory_limit_bytes": MEMORY, "memory_peak_bytes": peak, "mounts": mounts, "networks": sorted(networks)}
        self.state.setdefault("snapshots", {})[phase] = result
        self.save()
        return result

    def run(self):
        self.local_docker()
        require(self.state.get("prepared"), "Falta preparacion")
        control = DevelopmentTrial(control=True)
        a, b = self.config(), control.config()
        require(a["services"]["db"]["environment"]["MYSQL_PASSWORD"] != b["services"]["db"]["environment"]["MYSQL_PASSWORD"], "Claves compartidas")
        require({v["name"] for v in a["volumes"].values()}.isdisjoint(v["name"] for v in b["volumes"].values()), "Volumenes compartidos")
        self.command(["docker", "pull", IMAGE], "descargar la imagen aprobada", timeout=240, diagnose_pull=True)
        validate_image(json.loads(self.command(["docker", "image", "inspect", IMAGE], "identidad GHCR"))[0])
        self.command(["docker", "pull", MYSQL_IMAGE], "MySQL 8.4 por digest ya acreditado", timeout=240)
        self.state["mysql_repo_digests"] = json.loads(self.command(["docker", "image", "inspect", MYSQL_IMAGE], "identidad MySQL"))[0].get("RepoDigests", [])
        self.checked("identity", {"rebuilt": False, "republished": False, "image_id": IMAGE_ID})
        up = ["up", "-d", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180"]
        for trial in (self, control):
            self.command(trial.compose + up, "arrancar exclusivamente proyecto sintetico", timeout=240)
            trial.probe("read")
            trial.state["fixture"] = trial.probe("seed")
            trial.save()
            trial.marker(create=True)
        before, witness = self.snapshot("initial"), control.snapshot("initial")
        network = json.loads(self.command(["docker", "network", "inspect", self.project + "_dev_data"], "red interna"))[0]
        require(network["Internal"] is True, "MySQL no esta en una red interna")
        control_ip = control.inspect("db")["NetworkSettings"]["Networks"][control.project + "_dev_data"]["IPAddress"]
        require(bool(re.fullmatch(r"[0-9.]+", control_ip)), "IP del testigo invalida")
        self.command(self.compose + ["exec", "-T", "api", "python", "-c",
            "import socket,sys\ntry:\n socket.create_connection((sys.argv[1],3306),timeout=3)\nexcept OSError:\n pass\nelse:\n raise AssertionError('Red de otro proyecto accesible')", control_ip], "bloqueo entre redes sinteticas")
        self.checked("isolation", {"two_distinct_projects": True, "independent_sql_uploads_credentials_networks": True, "cross_project_tcp_blocked": True})
        self.checked("web_origin", json.loads(self.command(self.compose + ["exec", "-T", "api", "python", "-c", WEB], "Web y origen development")))
        self.command(self.compose + up + ["--force-recreate"], "recrear solo development sintetico", timeout=240)
        after = self.snapshot("recreated")
        require(all(before[s]["container_id"] != after[s]["container_id"] and before[s]["mounts"] == after[s]["mounts"] for s in VOLUMES), "Recreacion/persistencia no demostrada")
        self.probe("restored")
        self.marker()
        self.checked("persistence", "SQL, PNG y marcador conservados tras recrear API y MySQL sinteticos")
        self.command(self.compose + ["stop", "db"], "detener solo MySQL sintetico")
        self.probe("degraded")
        self.wait_state("api", "unhealthy")
        self.command(self.compose + ["start", "db"], "recuperar MySQL sintetico")
        self.wait_state("db", "healthy")
        self.wait_state("api", "healthy")
        stable = self.snapshot("before_fault")
        self.checked("dependency", "Sin MySQL: HTTP 503 y API unhealthy; recuperacion a healthy")
        fault = self.private / "fault.compose.json"
        fault.write_text(json.dumps({"services": {"api": {"command": ["python", "-c", "raise SystemExit(1)"], "restart": "no"}}}))
        # Mismo up global observado en Dokploy. --build no construye nada:
        # ambos servicios tienen solo image por digest y ningun contexto build.
        panel_up = ["up", "-d", "--build", "--remove-orphans"]
        self.command(self.compose + ["-f", str(fault)] + panel_up, "fallo controlado con up equivalente al panel", timeout=120)
        deadline = time.monotonic() + 30
        while self.inspect("api")["State"]["Running"] and time.monotonic() < deadline:
            time.sleep(1)
        failed = self.inspect("api")
        require(not failed["State"]["Running"] and failed["State"]["ExitCode"] == 1, "No se acredito el fallo de API")
        self.command(self.compose + panel_up + ["--wait", "--wait-timeout", "180"], "rollback equivalente al panel", timeout=240)
        recovered = self.snapshot("rollback")
        db_identity = ("container_id", "started_at", "restart_count", "image_id", "memory_limit_bytes", "mounts", "networks")
        require(all(recovered["db"][k] == stable["db"][k] for k in db_identity), "Rollback altero MySQL")
        require(recovered["api"]["container_id"] != failed["Id"] and recovered["api"]["mounts"] == stable["api"]["mounts"], "Rollback no restauro API/volumen")
        self.probe("restored")
        self.marker()
        control.probe("restored")
        control.marker()
        final_control = control.snapshot("after_trial")
        require(all(final_control[s]["container_id"] == witness[s]["container_id"] and final_control[s]["started_at"] == witness[s]["started_at"] and final_control[s]["mounts"] == witness[s]["mounts"] for s in VOLUMES), "Se altero el proyecto testigo")
        self.checked("rollback_panel", {"same_approved_image": True, "failed_configuration_reverted": True, "db_unchanged": True,
                                        "panel_equivalent_argv": panel_up, "no_build_contexts": True,
                                        "control_project_unchanged": True, "different_image_compatibility_verified": False})
        self.checked("memory", {"development_limit_bytes": 2 * MEMORY, "production_declared_limit_bytes": 2 * MEMORY,
                                "required_team_memory_bytes": 4 * MEMORY, "required_team_containers": 4,
                                "institutional_quota_verified": False, "capacity_on_institutional_server_verified": False})

    def cleanup(self):
        try:
            control = DevelopmentTrial(control=True)
            if control.state.get("prepared"):
                Trial.cleanup(control)
        finally:
            Trial.cleanup(self)

    def report(self):
        self.state.update(passed=all(self.state["checks"].get(k, {}).get("status") == "CUMPLE" for k in CHECKS) and not self.state.get("failure"),
                          dokploy_modified=False, institutional_deployment_authorized=False, institutional_quota_verified=False,
                          production_recovery_verified=False, production_deployment_blocked=True)
        out = ROOT / "artifacts/development-web"
        out.mkdir(parents=True, exist_ok=True)
        (out / "resultado.json").write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n")
        require(self.state["passed"], "Ensayo development incompleto; consultar resultado.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "run", "cleanup", "report"))
    args = parser.parse_args()
    trial = DevelopmentTrial()
    try:
        getattr(trial, args.phase)()
    except (TrialError, OSError, ValueError, LookupError, TypeError) as error:
        trial.state.setdefault("failure", args.phase + ": " + (str(error) if isinstance(error, TrialError) else type(error).__name__))
        trial.save()
        print("FAIL " + trial.state["failure"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
