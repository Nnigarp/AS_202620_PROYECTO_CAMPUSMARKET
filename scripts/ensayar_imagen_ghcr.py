"""Ensayo exclusivo del runner GitHub alojado; nunca usa endpoints de Dokploy.

Python estandar en el host. El probe usa solo dependencias ya incluidas en la
imagen aprobada. El JSON de evidencia excluye Environment, cuerpos y sesiones.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import time
from pathlib import Path

from scripts.preparar_despliegue_web import IMAGE
from scripts.preparar_despliegue_web import SOURCE as SOURCE_SHA

REPOSITORY = "ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET"
ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "deploy/compose.prod.yaml"
VOLUMES = {"api": ("publication_images", "/app/backend/uploads"), "db": ("mysql_data", "/var/lib/mysql")}
CRITERIA = {
    "compose": "Compose validado y sin build",
    "pull": "Descarga real del digest con acceso GHCR",
    "identity": "Imagen, OCI, REVISION y encabezado corresponden al SHA fuente",
    "health": "API y MySQL saludables; conexion SQL real",
    "functional": "Lecturas HTTP no destructivas en API aislada",
    "synthetic": "Base nueva y fixtures completamente sinteticos",
    "dependency": "Sin MySQL: HTTP 503 y healthcheck unhealthy; recuperacion",
    "persistence": "SQL y uploads sobreviven a recrear los dos contenedores",
    "no_build": "Misma imagen descargada antes y despues; sin reconstruccion",
    "cleanup": "Sin contenedores, volumenes ni redes propios restantes",
}

# Se ejecuta en memoria dentro de api. No escribe codigo de la aplicacion.
PROBE = r'''
import hashlib, io, json, os, secrets, sys, urllib.error, urllib.request
from PIL import Image
from backend.app.db import transaction

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
data = json.load(sys.stdin)
assert os.environ["CAMPUSMARKET_DB_HOST"] == "db"
assert os.environ["CAMPUSMARKET_DB_NAME"] == data["database"]
assert data["database"].endswith("_test")
revisions = set()

def request(method, path, expected, payload=None, token=None, body=None, content_type=None):
    assert path.startswith("/") and not path.startswith("//") and "://" not in path
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request("http://127.0.0.1:8000" + path, data=body, headers=headers, method=method)
    try:
        response = opener.open(req, timeout=15)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        assert response.status == expected, "Estado HTTP inesperado"
        revision = response.headers.get("X-CampusMarket-Revision")
        assert revision == data["source_sha"], "Revision HTTP inesperada"
        revisions.add(revision)
        raw = response.read()
        return json.loads(raw) if "application/json" in response.headers.get("Content-Type", "") else raw

mode = data["mode"]
if mode == "degraded":
    assert request("GET", "/health", 503)["status"] == "degraded"
    result = {"status": 503}
elif mode == "read":
    assert request("GET", "/health", 200)["status"] == "ok"
    schema = request("GET", "/openapi.json", 200)
    assert {"/health", "/catalogo", "/usuarios/registro"} <= schema["paths"].keys()
    assert request("GET", "/catalogo", 200) == [], "La base del ensayo debe estar vacia"
    with transaction() as cursor:
        cursor.execute("SELECT DATABASE() AS db, VERSION() AS version")
        server = cursor.fetchone()
    assert server["db"] == data["database"]
    assert server["version"].startswith("8.4.")
    result = {"http_status": 200, "http_revisions": sorted(revisions), "database": server["db"], "mysql_version": server["version"]}
elif mode == "seed":
    credentials = {"correo": secrets.token_hex(16) + "@example.test", "password": secrets.token_urlsafe(24)}
    user = request("POST", "/usuarios/registro", 201, payload={"nombre": "Ensayo sintetico GHCR", **credentials})
    session = request("POST", "/usuarios/login", 200, payload=credentials)
    assert session["usuario"]["id"] == user["id"]
    publication = request("POST", "/publicaciones", 201, token=session["access_token"], payload={
        "titulo": "Fixture sintetico GHCR", "descripcion": "Dato efimero exclusivo del runner",
        "precio": 1.25, "modalidad": "venta", "estado": "usado",
    })
    png = io.BytesIO()
    Image.new("RGB", (32, 24), "#7257ec").save(png, format="PNG")
    boundary = "CampusMarket" + secrets.token_hex(12)
    body = ("--" + boundary + '\r\nContent-Disposition: form-data; name="archivo"; filename="fixture.png"\r\n'
            "Content-Type: image/png\r\n\r\n").encode() + png.getvalue() + ("\r\n--" + boundary + "--\r\n").encode()
    image = request("POST", "/publicaciones/" + str(publication["id"]) + "/imagenes", 201,
                    token=session["access_token"], body=body, content_type="multipart/form-data; boundary=" + boundary)
    content = request("GET", image["imagen_url"], 200)
    result = {"publication_id": publication["id"], "owner_id": user["id"], "image_path": image["imagen_url"],
              "image_sha256": hashlib.sha256(content).hexdigest()}
elif mode == "restored":
    fixture = data["fixture"]
    publication = request("GET", "/catalogo/" + str(fixture["publication_id"]), 200)
    assert publication["propietario_id"] == fixture["owner_id"]
    assert any(image["imagen_url"] == fixture["image_path"] for image in publication["imagenes"])
    assert hashlib.sha256(request("GET", fixture["image_path"], 200)).hexdigest() == fixture["image_sha256"]
    result = {"sql_persisted": True, "uploads_persisted": True}
else:
    raise AssertionError("Modo de probe desconocido")
print(json.dumps(result))
'''


class TrialError(RuntimeError):
    """Solo mensajes definidos aqui: nunca stdout/stderr con secretos."""


def require(condition, message):
    if not condition:
        raise TrialError(message)


def classify_pull_error(stderr):
    """Categoria orientativa por patrones; nunca devuelve texto de Docker."""
    text = stderr.lower()
    patterns = (
        ("PLATFORM_MISMATCH", ("no matching manifest", "no match for platform")),
        ("REFERENCE_NOT_FOUND", ("manifest unknown", "manifest_unknown", "name unknown", "name_unknown", "404 not found")),
        ("AUTHENTICATION", ("unauthorized", "authentication required")),
        ("AUTHORIZATION", ("denied:", "access denied", "insufficient_scope", "forbidden")),
        ("RATE_LIMIT", ("toomanyrequests", "too many requests")),
        ("INVALID_REFERENCE", ("invalid reference format", "invalid checksum digest")),
        ("DAEMON_UNAVAILABLE", ("cannot connect to the docker daemon", "is the docker daemon running")),
        ("NETWORK", ("no such host", "network is unreachable", "connection refused", "connection reset", "i/o timeout", "context deadline exceeded", "tls handshake timeout", "dial tcp")),
        ("TLS", ("x509:", "certificate verify failed", "tls:")),
        ("REGISTRY_SERVER", ("500 internal server error", "502 bad gateway", "503 service unavailable", "504 gateway timeout")),
        ("STORAGE", ("no space left on device",)),
    )
    category = next((category for category, markers in patterns if any(marker in text for marker in markers)), "UNKNOWN")
    if category == "UNKNOWN" and "failed to resolve reference" in text and ": not found" in text:
        return "REFERENCE_NOT_FOUND"
    return category


def project_from_environment(env):
    require(env.get("GITHUB_ACTIONS") == "true" and env.get("RUNNER_ENVIRONMENT") == "github-hosted", "Requiere runner efimero alojado por GitHub")
    require(env.get("GITHUB_REPOSITORY") in {REPOSITORY, "Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET"}, "Repositorio de ensayo inesperado")
    require(env.get("GITHUB_SERVER_URL") == "https://github.com", "Servidor GitHub inesperado")
    require(not env.get("DOCKER_HOST") and env.get("DOCKER_CONTEXT", "default") in {"", "default"}, "No se admiten conexiones Docker remotas")
    require(re.fullmatch(r"[0-9]+", env.get("GITHUB_RUN_ID", "")) and re.fullmatch(r"[0-9]+", env.get("GITHUB_RUN_ATTEMPT", "")), "Identidad de run invalida")
    require(re.fullmatch(r"[0-9a-f]{40}", env.get("GITHUB_SHA", "")), "SHA del workflow invalido")
    return "campusmarket-ghcr-" + env["GITHUB_RUN_ID"] + "-" + env["GITHUB_RUN_ATTEMPT"]


def validate_config(config, project, database):
    require(config.get("name") == project and set(config.get("services", {})) == {"api", "db"}, "Proyecto o servicios inesperados")
    require(config["services"]["api"].get("image") == IMAGE, "Compose no fija el digest aprobado")
    require(config["services"]["db"].get("image") == "mysql:8.4", "Se requiere MySQL 8.4")
    require(set(config.get("volumes", {})) == {"mysql_data", "publication_images"}, "Volumenes inesperados")
    require(not config.get("configs") and not config.get("secrets"), "No se admiten archivos externos al ensayo")
    require(set(config.get("networks", {})) == {"default"}, "Redes inesperadas")
    network = config["networks"]["default"]
    require(not network.get("external") and network.get("name") == project + "_default", "La red no esta aislada")
    for service, (volume, destination) in VOLUMES.items():
        cfg = config["services"][service]
        require(not any(cfg.get(key) for key in ("build", "ports", "privileged", "cap_add", "container_name", "network_mode", "pid", "devices", "volumes_from", "external_links")), "Configuracion de servicio no permitida")
        require(set(cfg.get("networks", {})) == {"default"}, "Servicio fuera de la red del ensayo")
        mounts = cfg.get("volumes", [])
        require(len(mounts) == 1 and mounts[0].get("type") == "volume" and mounts[0].get("source") == volume and mounts[0].get("target") == destination and not mounts[0].get("read_only"), "Montaje de servicio inesperado")
        root_volume = config["volumes"][volume]
        require(not root_volume.get("external") and not root_volume.get("driver_opts") and root_volume.get("name") == project + "_" + volume, "Se requiere un volumen nuevo propio")
        require(bool(cfg.get("healthcheck", {}).get("test")), "Falta healthcheck")
    api_env = config["services"]["api"]["environment"]
    db_env = config["services"]["db"]["environment"]
    require(api_env["CAMPUSMARKET_DB_HOST"] == "db" and api_env["CAMPUSMARKET_DB_NAME"] == database and db_env["MYSQL_DATABASE"] == database, "La API debe usar exclusivamente la base de prueba")


class Trial:
    def __init__(self):
        self.project = project_from_environment(os.environ)
        self.database = self.project.replace("-", "_") + "_test"
        temp = Path(os.environ["RUNNER_TEMP"])
        require(temp.is_absolute(), "RUNNER_TEMP debe ser absoluto")
        self.private = temp / self.project
        self.env_file = self.private / "compose.env"
        self.state_file = self.private / "state.json"
        self.state = json.loads(self.state_file.read_text()) if self.state_file.exists() else {
            "repository": os.environ["GITHUB_REPOSITORY"], "workflow_commit": os.environ["GITHUB_SHA"], "source_commit": SOURCE_SHA,
            "image": IMAGE, "project": self.project, "run_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
            "run": "https://github.com/" + os.environ["GITHUB_REPOSITORY"] + "/actions/runs/" + os.environ["GITHUB_RUN_ID"], "checks": {},
        }
        require(self.state["project"] == self.project and self.state["workflow_commit"] == os.environ["GITHUB_SHA"], "Estado de otro ensayo")
        self.compose = ["docker", "compose", "--project-name", self.project, "--env-file", str(self.env_file), "-f", str(COMPOSE_FILE)]

    def save(self):
        self.private.mkdir(mode=0o700, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def command(self, args, operation, stdin=None, timeout=60, diagnose_pull=False):
        try:
            result = subprocess.run(args, input=stdin, text=True, capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            if diagnose_pull:
                self.state["docker_pull_error"] = {"category": "TIMEOUT", "exit_code": None}
                self.save()
            raise TrialError("Tiempo agotado en " + operation) from None
        if result.returncode != 0:
            message = "Fallo de infraestructura: " + operation
            if diagnose_pull:
                category = classify_pull_error(result.stderr)
                self.state["docker_pull_error"] = {"category": category, "exit_code": result.returncode}
                self.save()
                message += f" [Docker pull: {category}; exit={result.returncode}]"
            raise TrialError(message)
        return result.stdout

    def local_docker(self):
        endpoint = self.command(["docker", "context", "inspect", "default", "--format", "{{.Endpoints.docker.Host}}"], "contexto Docker").strip()
        require(endpoint == "unix:///var/run/docker.sock", "Solo se admite el daemon local del runner")

    def inventory(self):
        label = "label=com.docker.compose.project=" + self.project
        return {
            "containers": self.command(["docker", "ps", "-aq", "--filter", label], "inventario de contenedores").split(),
            "volumes": self.command(["docker", "volume", "ls", "-q", "--filter", label], "inventario de volumenes").split(),
            "networks": self.command(["docker", "network", "ls", "-q", "--filter", label], "inventario de redes").split(),
        }

    def checked(self, key, result=None):
        self.state["checks"][key] = {"status": "CUMPLE", "result": result or "Verificacion real satisfactoria"}
        self.state.pop("active_check", None)
        self.save()
        print("PASS " + key)

    def begin(self, key):
        self.state["active_check"] = key
        self.save()

    def config(self):
        config = json.loads(self.command(self.compose + ["config", "--format", "json"], "validacion Compose"))
        validate_config(config, self.project, self.database)

    def prepare(self):
        self.local_docker()
        require(not self.private.exists(), "Ya existe un directorio de ensayo: no se sobrescribe")
        require(not any(self.inventory().values()), "Ya existen recursos con este proyecto: no se reutilizan")
        self.save()
        values = {"MYSQL_ROOT_PASSWORD": secrets.token_hex(24), "MYSQL_PASSWORD": secrets.token_hex(24),
                  "MYSQL_DATABASE": self.database, "MYSQL_USER": "campusmarket_ghcr", "CAMPUSMARKET_ADMIN_USER_IDS": ""}
        for key in ("MYSQL_ROOT_PASSWORD", "MYSQL_PASSWORD"):
            print("::add-mask::" + values[key])
        fd = os.open(self.env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write("\n".join(key + "=" + value for key, value in values.items()) + "\n")
        self.begin("compose")
        self.config()
        self.state["prepared"] = True
        self.state["tools"] = {
            "docker": self.command(["docker", "version", "--format", "{{.Client.Version}} / {{.Server.Version}}"], "version Docker").strip(),
            "compose": self.command(["docker", "compose", "version", "--short"], "version Compose").strip(),
        }
        self.state["compose_sha256"] = hashlib.sha256(COMPOSE_FILE.read_bytes()).hexdigest()
        self.checked("compose")

    def probe(self, mode):
        data = {"mode": mode, "source_sha": SOURCE_SHA, "database": self.database, "fixture": self.state.get("fixture")}
        raw = self.command(self.compose + ["exec", "-T", "api", "python", "-c", PROBE], "probe " + mode, stdin=json.dumps(data), timeout=45)
        return json.loads(raw)

    def inspect(self, service):
        cid = self.command(self.compose + ["ps", "-aq", service], "identificar " + service).strip()
        require(bool(re.fullmatch(r"[0-9a-f]{12,64}", cid)), "Falta un contenedor unico")
        data = json.loads(self.command(["docker", "inspect", cid], "inspeccionar " + service))[0]
        require(data["Config"]["Labels"]["com.docker.compose.project"] == self.project, "Contenedor fuera del proyecto")
        return data

    def wait_state(self, service, expected, timeout=150):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            data = self.inspect(service)
            if data["State"].get("Health", {}).get("Status") == expected:
                return
            time.sleep(2)
        raise TrialError("Healthcheck no alcanzo " + expected + " para " + service)

    def snapshot(self, phase):
        snapshot = {}
        for service, (volume, destination) in VOLUMES.items():
            data = self.inspect(service)
            require(data["State"]["Running"] and data["State"]["Health"]["Status"] == "healthy" and not data["State"]["OOMKilled"], "Contenedor no saludable")
            require(data["HostConfig"]["Memory"] == 256 * 1024 * 1024 and data["HostConfig"]["NanoCpus"] == 500_000_000, "Cuota efectiva inesperada")
            mounts = [{"Name": m.get("Name"), "Destination": m["Destination"], "RW": m["RW"]} for m in data["Mounts"]]
            require(mounts == [{"Name": self.project + "_" + volume, "Destination": destination, "RW": True}], "Montajes efectivos inesperados")
            if service == "api":
                require(data["Image"] == self.state["image_id"] and data["Config"]["Image"] == IMAGE, "API no ejecuta la imagen descargada")
                require(data["Config"]["Labels"].get("org.opencontainers.image.revision") == SOURCE_SHA, "OCI del contenedor incorrecta")
                revision = self.command(self.compose + ["exec", "-T", "api", "cat", "/app/REVISION"], "leer REVISION").strip()
                require(revision == SOURCE_SHA, "REVISION no corresponde al commit fuente")
            snapshot[service] = {"container_id": data["Id"], "image_id": data["Image"], "image_reference": data["Config"]["Image"],
                                 "health": "healthy", "memory_bytes": data["HostConfig"]["Memory"], "mounts": mounts}
            if service == "api":
                snapshot[service].update(oci_revision=data["Config"]["Labels"]["org.opencontainers.image.revision"], revision_file=revision)
        self.state.setdefault("snapshots", {})[phase] = snapshot
        self.save()
        return snapshot

    def run(self):
        self.local_docker()
        require(self.state.get("prepared"), "Falta preparacion validada")
        self.config()
        self.begin("pull")
        self.command(["docker", "pull", IMAGE], "descargar digest GHCR", timeout=240, diagnose_pull=True)
        image = json.loads(self.command(["docker", "image", "inspect", IMAGE], "inspeccionar imagen"))[0]
        require(IMAGE in image.get("RepoDigests", []) and image["Config"]["Labels"].get("org.opencontainers.image.revision") == SOURCE_SHA, "Digest o etiqueta remota incorrectos")
        self.state["image_id"] = image["Id"]
        self.checked("pull", "Digest exacto descargado; RepoDigests y etiqueta comprobados")
        self.begin("health")
        self.command(["docker", "pull", "mysql:8.4"], "descargar MySQL 8.4", timeout=240)
        mysql = json.loads(self.command(["docker", "image", "inspect", "mysql:8.4"], "identidad MySQL"))[0]
        self.state["mysql_repo_digests"] = mysql.get("RepoDigests", [])
        self.command(self.compose + ["up", "-d", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180"], "arrancar Compose", timeout=240)
        self.begin("identity")
        before = self.snapshot("initial")
        self.begin("health")
        self.checked("health", self.probe("read"))
        self.checked("identity")
        self.checked("functional", "GET /health, /openapi.json y /catalogo: HTTP 200")
        self.begin("synthetic")
        self.state["fixture"] = self.probe("seed")
        self.checked("synthetic", "Base inicialmente vacia; un usuario, una publicacion y un PNG generados en el runner")
        self.begin("dependency")
        self.command(self.compose + ["stop", "db"], "detener exclusivamente db sintetica")
        self.probe("degraded")
        self.wait_state("api", "unhealthy")
        self.command(self.compose + ["start", "db"], "recuperar db sintetica")
        self.wait_state("db", "healthy")
        self.wait_state("api", "healthy")
        self.probe("restored")
        self.checked("dependency", "MySQL detenida: HTTP 503 y API unhealthy; al arrancarla ambos vuelven a healthy")
        self.begin("persistence")
        self.command(self.compose + ["up", "-d", "--no-build", "--pull", "never", "--force-recreate", "--wait", "--wait-timeout", "180"], "recrear exclusivamente el proyecto sintetico", timeout=240)
        after = self.snapshot("recreated")
        require(all(before[s]["container_id"] != after[s]["container_id"] and before[s]["mounts"] == after[s]["mounts"] for s in VOLUMES), "No se acredito recreacion conservando volumenes")
        self.checked("persistence", self.probe("restored"))
        self.checked("no_build", "Sin build en Compose, --no-build en ambos arranques e Image ID conservado")

    def cleanup(self):
        previous_check = self.state.pop("active_check", None)
        if previous_check and previous_check not in self.state["checks"]:
            self.state["checks"][previous_check] = {"status": "NO CUMPLE", "result": "La fase no termino satisfactoriamente"}
        cleaned = None
        try:
            self.local_docker()
            if self.state.get("prepared"):
                self.begin("cleanup")
                if any(self.inventory().values()):
                    self.config()
                    self.command(self.compose + ["down", "--volumes", "--remove-orphans"], "cleanup del proyecto de este run", timeout=120)
                remaining = self.inventory()
                require(not any(remaining.values()), "Quedan recursos del ensayo")
                cleaned = remaining
        finally:
            self.env_file.unlink(missing_ok=True)
            config = Path(os.environ.get("DOCKER_CONFIG", ""))
            expected_config = Path(os.environ["RUNNER_TEMP"]) / ("campusmarket-ghcr-docker-" + os.environ["GITHUB_RUN_ID"] + "-" + os.environ["GITHUB_RUN_ATTEMPT"])
            require(config == expected_config, "Ruta Docker de credenciales inesperada")
            if config.exists():
                shutil.rmtree(config)
        if cleaned is not None:
            self.checked("cleanup", {**cleaned, "temporary_credentials_removed": True})

    def report(self):
        out = ROOT / "artifacts/ensayo-ghcr"
        out.mkdir(parents=True, exist_ok=True)
        self.state["passed"] = all(self.state["checks"].get(key, {}).get("status") == "CUMPLE" for key in CRITERIA) and not self.state.get("failure")
        (out / "resultado.json").write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        lines = ["# Ensayo real GHCR", "", "- Commit fuente: `" + SOURCE_SHA + "`", "- Imagen: `" + IMAGE + "`",
                 "- Commit del workflow: `" + self.state["workflow_commit"] + "`", "- Run: " + self.state["run"], "",
                 "| Criterio | Estado | Archivo/linea | Commit | Run | Resultado |", "|---|---|---|---|---|---|"]
        source_lines = Path(__file__).read_text(encoding="utf-8").splitlines()
        for key, title in CRITERIA.items():
            item = self.state["checks"].get(key, {"status": "BLOQUEADO", "result": "Sin verificacion real satisfactoria en este run"})
            line = next(i for i, text in enumerate(source_lines, 1) if 'self.checked("' + key + '"' in text)
            result = json.dumps(item["result"], ensure_ascii=False).replace("|", "/")
            link = "https://github.com/" + REPOSITORY + "/blob/" + self.state["workflow_commit"] + "/scripts/ensayar_imagen_ghcr.py#L" + str(line)
            lines.append(f"| {title} | {item['status']} | [verificacion:{line}]({link}) | {self.state['workflow_commit']} | {self.state['run']} | {result} |")
        if self.state.get("failure"):
            lines += ["", "Fallo: " + self.state["failure"]]
        text = "\n".join(lines) + "\n"
        (out / "matriz.md").write_text(text, encoding="utf-8")
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
                stream.write(text)
        require(self.state["passed"], "Ensayo incompleto: consultar matriz y checks")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "run", "cleanup", "report"))
    args = parser.parse_args()
    trial = Trial()
    try:
        getattr(trial, args.phase)()
    except (TrialError, OSError, ValueError, LookupError, TypeError, subprocess.SubprocessError) as error:
        # No se publica el mensaje de librerias, comandos o respuestas HTTP.
        message = str(error) if isinstance(error, TrialError) else type(error).__name__
        trial.state.setdefault("failure", args.phase + ": " + message)
        trial.state.setdefault("failures", []).append(args.phase + ": " + message)
        key = trial.state.pop("active_check", None)
        if key:
            trial.state["checks"][key] = {"status": "NO CUMPLE", "result": message}
        trial.save()
        print("FAIL " + trial.state["failure"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
