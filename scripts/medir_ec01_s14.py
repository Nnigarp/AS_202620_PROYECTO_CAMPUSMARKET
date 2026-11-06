"""EC-01 reproducible: imagen vigente, MySQL sintético y Chrome, solo en CI efímero."""
import argparse
import hashlib
import importlib.metadata
import ipaddress
import json
import math
import os
import platform
import re
import secrets
import statistics
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "d5b8b500e309e5997a6063f20b6c7da6682ef785"
RUNTIME = "46ede525602161826b75273fbb12528e739908cc"
IMAGE = "ghcr.io/nnigarp/campusmarket-web-universidades@sha256:11d92aa9b66f1a4c6b879a6e8cd62cc3c102a37c034a44cbde27442b73694fa7"
LOCAL = "http://127.0.0.1:8000"
PUBLIC_HOST = "campusmarket.iscoutb.dev"
BACKEND = None
OUT = ROOT / "artifacts/s14"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def guard():
    require(os.getenv("GITHUB_ACTIONS") == "true", "Exige runner efímero GitHub Actions.")
    require(os.getenv("GITHUB_REPOSITORY") in {
        "Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET", "ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET"
    }, "Repositorio no autorizado para este ensayo.")
    run, attempt = os.getenv("GITHUB_RUN_ID", ""), os.getenv("GITHUB_RUN_ATTEMPT", "")
    require(run.isdigit() and attempt.isdigit(), "Identidad de runner inválida.")
    require(os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock") == "unix:///var/run/docker.sock",
            "No admite daemon remoto.")
    return f"cm-s14-{run}-{attempt}"


def private_state():
    return Path(os.environ["RUNNER_TEMP"]) / (guard() + ".json")


def command(args, stdin=None):
    result = subprocess.run(args, input=stdin, text=True, capture_output=True, check=False, cwd=ROOT)
    require(result.returncode == 0, f"Operación aislada falló (exit {result.returncode}); no se publica salida privada.")
    return result.stdout.strip()


def compose(state, *args):
    require(state["project"] == guard(), "Proyecto ajeno: operación rechazada.")
    return command(["docker", "compose", "-p", state["project"], "-f", state["compose"], *args])


def request(path, payload=None):
    require(path.startswith("/") and not path.startswith("//") and "://" not in path, "Ruta no local rechazada.")
    require(BACKEND is not None, "La API debe identificarse en el proyecto privado antes de HTTP.")
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BACKEND + path, data=data,
                                 headers={"Content-Type": "application/json"} if data else {})
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.read(), response.headers


def summarize(samples):
    require(len(samples) == 10, "Se requieren diez observaciones, sin descartar muestras.")
    times = sorted(x["ms"] for x in samples)
    within = sum(x["valid"] and x["ms"] <= 2000 for x in samples)
    return {"samples": samples, "within_2000ms": within, "required": 9, "repetitions": 10,
            "median_ms": round(statistics.median(times), 3), "p95_ms": times[math.ceil(.95 * len(times)) - 1],
            "outcome": "CUMPLE EN ENTORNO AISLADO" if within >= 9 else "NO CUMPLE",
            "errors": sum(not x["valid"] for x in samples)}


def prepare():
    project = guard()
    require(not private_state().exists(), "Estado previo: no sobrescribir.")
    source = command(["git", "rev-parse", "HEAD"])
    require(source == os.environ.get("GITHUB_SHA"), "Checkout no corresponde al run.")
    command(["git", "merge-base", "--is-ancestor", BASE, source])
    command(["git", "fetch", "--no-tags", "https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET.git", RUNTIME])
    require(not command(["git", "diff", "--name-only", RUNTIME, source, "--", "backend/app", "frontend/campusmarket/lib", "contracts"]),
            "Código funcional distinto a la imagen: no se extrapola la medición.")
    require(not command(["docker", "ps", "-aq", "--filter", "label=com.docker.compose.project=" + project]), "Proyecto ocupado.")
    directory = Path(tempfile.mkdtemp(prefix=project + "-", dir=os.environ["RUNNER_TEMP"]))
    env = directory / "synthetic.env"
    values = {"MYSQL_ROOT_PASSWORD": secrets.token_hex(24), "MYSQL_PASSWORD": secrets.token_hex(24),
              "MYSQL_DATABASE": "campusmarket_s14_test", "MYSQL_USER": "campusmarket_app",
              "CAMPUSMARKET_CORS_ORIGINS": LOCAL}
    env.write_text("\n".join(k + "=" + v for k, v in values.items()) + "\n")
    env.chmod(0o600)
    config = json.loads(command(["docker", "compose", "-p", project, "--env-file", str(env),
                                 "-f", str(ROOT / "deploy/compose.prod.yaml"), "config", "--format", "json"]))
    require(set(config["services"]) == {"api", "db"}, "Solo api y db.")
    require(config["services"]["api"]["image"] == IMAGE, "Digest distinto al acreditado.")
    for service in config["services"].values():
        require(not service.get("ports") and not service.get("build") and not service.get("privileged"), "Stack de origen inesperado.")
    require(set(config["volumes"]) == {"mysql_data", "publication_images"}, "Volúmenes inesperados.")
    for volume in config["volumes"].values():
        require(not volume.get("external") and volume["name"].startswith(project + "_"), "Volumen ajeno.")
    require(len(config["networks"]) == 1 and not config["networks"]["default"].get("external"), "Red externa rechazada.")
    config["networks"]["default"]["internal"] = True
    config["services"]["api"]["environment"]["CAMPUSMARKET_S14_SYNTHETIC"] = "true"
    mysql = os.getenv("S14_MYSQL_DIGEST", "mysql:8.4")
    require(mysql == "mysql:8.4" or re.fullmatch(r"mysql@sha256:[0-9a-f]{64}", mysql), "Referencia MySQL inválida.")
    config["services"]["db"]["image"] = mysql
    path = directory / "compose.json"
    path.write_text(json.dumps(config))
    path.chmod(0o600)
    state = {"project": project, "compose": str(path), "orchestration_sha": source}
    private_state().write_text(json.dumps(state))
    private_state().chmod(0o600)
    compose(state, "config", "--quiet")
    compose(state, "pull")
    image = json.loads(command(["docker", "image", "inspect", IMAGE]))[0]
    require(image["Config"]["Labels"].get("org.opencontainers.image.revision") == RUNTIME, "OCI distinta.")
    require(command(["docker", "run", "--rm", "--network", "none", "--entrypoint", "cat", IMAGE, "/app/REVISION"]) == RUNTIME,
            "Fichero REVISION distinto.")
    compose(state, "up", "-d", "--no-build", "--wait", "--wait-timeout", "180")
    api_id = compose(state, "ps", "-q", "api")
    api_data = json.loads(command(["docker", "inspect", api_id]))[0]
    select_backend(api_data)
    status, raw, headers = request("/health")
    require(status == 200 and json.loads(raw)["status"] == "ok", "Health sintético falló.")
    require(headers.get("X-CampusMarket-Revision") == RUNTIME, "Header distinto.")
    state["image_id"] = image["Id"]
    mysql_data = json.loads(command(["docker", "image", "inspect", mysql]))[0]
    state["mysql_digest"] = mysql_data["RepoDigests"][0]
    return state



def select_backend(api_data):
    global BACKEND
    labels = api_data["Config"]["Labels"]
    require(labels["com.docker.compose.project"] == guard(), "API ajena al proyecto: rechazada.")
    require(labels["com.docker.compose.service"] == "api", "Servicio distinto a API.")
    networks = api_data["NetworkSettings"]["Networks"]
    require(list(networks) == [guard() + "_default"], "Red ajena o adicional rechazada.")
    require(not api_data["HostConfig"]["PortBindings"], "No debe publicar puertos del ensayo.")
    address = networks[guard() + "_default"]["IPAddress"]
    require(ipaddress.ip_address(address).version == 4 and ipaddress.ip_address(address).is_private,
            "Dirección no privada rechazada.")
    BACKEND = "http://" + address + ":8000"


def seed(state):
    status, raw, _ = request("/catalogo")
    require(status == 200 and json.loads(raw) == [], "El catálogo sintético debe empezar vacío y con su esquema inicializado.")
    owner = json.loads(request("/usuarios/registro", {"nombre": "Usuario sintético S14", "correo": "fixture@s14.invalid",
                                                   "password": secrets.token_urlsafe(24)})[1])["id"]
    fixture = '''import os, json
from backend.app.db import transaction
assert os.environ.get("CAMPUSMARKET_S14_SYNTHETIC") == "true"
assert os.environ["CAMPUSMARKET_DB_NAME"] == "campusmarket_s14_test"
with transaction() as cursor:
    cursor.execute("SELECT COUNT(*) AS n FROM publicaciones")
    assert cursor.fetchone()["n"] == 0
    rows = [(f"Producto S14-G{(i-1)//100+1:02} {i:04}", "Datos sintéticos deterministas S14", 1000+i, OWNER) for i in range(1,1001)]
    cursor.executemany("INSERT INTO publicaciones (titulo,descripcion,precio,modalidad,estado,propietario_id) VALUES (%s,%s,%s,'venta','usado',%s)", rows)
    cursor.execute("SELECT COUNT(*) AS n FROM publicaciones")
    assert cursor.fetchone()["n"] == 1000
    print(json.dumps({"count":1000,"mysql_version":None,"titles_sha256":__import__('hashlib').sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}))
    cursor.execute("SELECT VERSION() AS version")
    print(cursor.fetchone()["version"])
'''.replace("OWNER", str(int(owner)))
    output = compose_exec(state, fixture).splitlines()
    dataset = json.loads(output[0])
    dataset["mysql_version"] = output[1]
    dataset.update({"groups": 10, "per_group": 100, "photos": 0, "universidad": None, "personal_data": False})
    return dataset


def compose_exec(state, source):
    require(state["project"] == guard(), "Proyecto ajeno.")
    wrapper = "import json, traceback\ntry:\n exec(compile(" + repr(source) + ", '<s14-fixture>', 'exec'), {})\nexcept Exception as error:\n details={'type':type(error).__name__, 'line':traceback.extract_tb(error.__traceback__)[-1].lineno, 'mysql_code':error.__cause__.args[0] if error.__cause__ and error.__cause__.args and isinstance(error.__cause__.args[0],int) else (error.args[0] if error.args and isinstance(error.args[0],int) else None)}\n print('S14_SAFE_ERROR='+json.dumps(details))\n"
    output = command(["docker", "compose", "-p", state["project"], "-f", state["compose"], "exec", "-T", "api", "python", "-"], stdin=wrapper)
    errors = [line for line in output.splitlines() if line.startswith("S14_SAFE_ERROR=")]
    require(not errors, "Fixture sintético rechazado: " + (errors[-1] if errors else ""))
    return output


def snapshot(state):
    services = {}
    ids = compose(state, "ps", "-q").splitlines()
    require(len(ids) == 2, "Número de contenedores distinto de dos.")
    for identifier in ids:
        item = json.loads(command(["docker", "inspect", identifier]))[0]
        labels = item["Config"]["Labels"]
        require(labels["com.docker.compose.project"] == guard(), "Contenedor ajeno.")
        require(item["HostConfig"]["Memory"] == 256 * 1024**2, "Límite de memoria distinto.")
        require(item["HostConfig"]["NanoCpus"] == 500000000, "Límite de CPU distinto.")
        services[labels["com.docker.compose.service"]] = {
            "id": item["Id"], "image_id": item["Image"], "healthy": item["State"]["Health"]["Status"],
            "oom": item["State"]["OOMKilled"], "restarts": item["RestartCount"],
            "memory_limit": item["HostConfig"]["Memory"], "nano_cpus": item["HostConfig"]["NanoCpus"],
            "memory_peak": int(command(["docker", "exec", identifier, "cat", "/sys/fs/cgroup/memory.peak"])),
            "mounts": [{"name": x.get("Name"), "target": x["Destination"]} for x in item["Mounts"]],
            "networks": list(item["NetworkSettings"]["Networks"])}
    return services


def http_measure():
    request("/catalogo?q=S14")  # Un warm-up separado y declarado.
    samples = []
    for index in range(1, 11):
        start = time.perf_counter()
        try:
            status, raw, _ = request("/catalogo?q=S14")
            rows = json.loads(raw)
            valid = status == 200 and isinstance(rows, list) and {x["id"] for x in rows} == set(range(1, 1001))
            sample = {"index": index, "status": status, "returned": len(rows), "valid": valid}
        except (OSError, ValueError, KeyError, TypeError) as error:
            sample = {"index": index, "valid": False, "error_type": type(error).__name__}
        sample["ms"] = round((time.perf_counter() - start) * 1000, 3)
        samples.append(sample)
    return summarize(samples)


def browser_measure():
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import expect, sync_playwright
    observed, blocked, browser_errors, started_queries = [], [], [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True,
                                     args=["--disable-dev-shm-usage", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        context = browser.new_context(viewport={"width": 1440, "height": 1600}, device_scale_factor=1,
                                      service_workers="block")
        def route_handler(route):
            req = route.request
            url = urllib.parse.urlsplit(req.url)
            if ((url.hostname == "127.0.0.1" and url.port == 8000) or url.hostname == PUBLIC_HOST) and req.method in {"GET", "OPTIONS", "HEAD"}:
                headers = {k: v for k, v in req.headers.items() if k.lower() not in {"host", "authorization", "cookie", "content-length"}}
                target = BACKEND + url.path + ("?" + url.query if url.query else "")
                if url.path == "/catalogo" and req.method == "GET":
                    started_queries.append(urllib.parse.parse_qs(url.query).get("q", [""])[0])
                response = context.request.fetch(target, method=req.method, headers=headers, max_redirects=0)
                if url.path == "/catalogo" and req.method == "GET":
                    rows = response.json()
                    observed.append({"query": urllib.parse.parse_qs(url.query).get("q", [""])[0],
                                     "status": response.status, "ids": [x["id"] for x in rows] if isinstance(rows, list) else [],
                                     "first_title": rows[0]["titulo"] if isinstance(rows, list) and rows else None})
                route.fulfill(response=response)
            elif (url.hostname in {"www.gstatic.com", "fonts.gstatic.com", "fonts.googleapis.com"} and req.method == "GET") or url.scheme in {"data", "blob"}:
                route.continue_()
            else:
                blocked.append({"host": url.hostname, "method": req.method})
                route.abort()
        context.route("**/*", route_handler)
        page = context.new_page()
        page.on("pageerror", lambda error: browser_errors.append(type(error).__name__))
        try:
            page.goto(LOCAL + "/app/", wait_until="domcontentloaded", timeout=90000)
            page.locator("flt-semantics-placeholder").wait_for(state="attached", timeout=90000)
            page.locator("flt-semantics-placeholder").evaluate("element => element.click()")
            page.get_by_text("Catálogo", exact=True).or_(page.get_by_label("Catálogo", exact=True)).first.click(timeout=90000, force=True)
            field = page.get_by_role("textbox").first
            button = page.get_by_role("button", name="Buscar en el catálogo", exact=True)
            field.wait_for(timeout=90000)
            page.get_by_text("Resultados (1000)", exact=True).or_(page.get_by_label("Resultados (1000)", exact=True)).first.wait_for(state="visible", timeout=90000)
            trace = {}
            def search(group):
                trace.clear()
                trace.update({"stage": "prepare_focus", "network_offset": len(observed), "started_offset": len(started_queries)})
                query = f"S14-G{group:02}"
                rectangle = field.bounding_box()
                require(rectangle is not None, "Buscador fuera del viewport.")
                page.mouse.click(rectangle["x"] + rectangle["width"] / 2, rectangle["y"] + rectangle["height"] / 2)
                page.wait_for_function("""() => {
                  let element = document.activeElement;
                  while (element && element.shadowRoot && element.shadowRoot.activeElement) element = element.shadowRoot.activeElement;
                  return element && ['INPUT','TEXTAREA'].includes(element.tagName);
                }""", timeout=10000)
                page.keyboard.press("Control+A")
                page.keyboard.type(query)
                page.wait_for_function("""expected => {
                  let element = document.activeElement;
                  while (element && element.shadowRoot && element.shadowRoot.activeElement) element = element.shadowRoot.activeElement;
                  return element && element.value === expected;
                }""", arg=query, timeout=10000)
                page.keyboard.press("Tab")
                page.wait_for_function("expected => [...document.querySelectorAll('input')].some(element => element.value === expected)", arg=query, timeout=10000)
                expect(field).to_have_value(query, timeout=10000)
                require(len(started_queries) == trace["started_offset"], "Se consultó antes del estímulo medido.")
                trace["stage"] = "await_response"
                page.evaluate("() => { window.__s14Start = null; window.addEventListener('pointerdown', () => { window.__s14Start = performance.now(); }, {capture:true, once:true}); }")
                with page.expect_response(lambda response: urllib.parse.urlsplit(response.url).path == "/catalogo" and urllib.parse.parse_qs(urllib.parse.urlsplit(response.url).query).get("q") == [query], timeout=30000):
                    button.click()
                begin = page.evaluate("window.__s14Start")
                require(isinstance(begin, (int, float)), "No se observó pointerdown del usuario.")
                response = next((x for x in reversed(observed) if x["query"] == query), None)
                require(response is not None, "El navegador no ejecutó la consulta esperada.")
                title = response["first_title"]
                trace["stage"] = "await_visible_results"
                results = page.get_by_text("Resultados (100)", exact=True).or_(page.get_by_label("Resultados (100)", exact=True)).first
                card = page.get_by_role("group", name=re.compile(re.escape(title))).first
                results.wait_for(state="visible", timeout=30000)
                card.wait_for(state="visible", timeout=30000)
                rectangle = card.bounding_box()
                require(rectangle is not None and rectangle["y"] >= 0 and rectangle["y"] + rectangle["height"] <= 1600,
                        "Primer resultado fuera del viewport: no se declara visible.")
                elapsed = page.evaluate("start => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve(performance.now()-start))))", begin)
                expected = set(range((group - 1) * 100 + 1, group * 100 + 1))
                return {"query": query, "ms": round(elapsed, 3), "status": response["status"],
                        "returned": len(response["ids"]), "first_visible_title": title,
                        "valid": response["status"] == 200 and set(response["ids"]) == expected}
            search(10)  # Warm-up de navegador; no forma parte de las diez muestras.
            samples = []
            for group in range(1, 11):
                start = time.perf_counter()
                try:
                    sample = search(group)
                except (PlaywrightError, RuntimeError, ValueError, KeyError, TypeError) as error:
                    sample = {"query": f"S14-G{group:02}", "ms": round((time.perf_counter()-start)*1000, 3),
                              "valid": False, "error_type": type(error).__name__, "error_stage": trace.get("stage"),
                              "observed_queries": [x["query"] for x in observed[trace.get("network_offset", 0):]]}
                sample["index"] = group
                samples.append(sample)
            page.screenshot(path=str(OUT / "chrome-final.png"))
            result = summarize(samples)
            if any(x.get("error_stage") == "prepare_focus" for x in samples):
                result["outcome"] = "NO CONCLUYENTE: falló preparación del observador"
            result.update({"browser": browser.version, "playwright": importlib.metadata.version("playwright"),
                           "viewport": [1440, 1600], "warmup": 1, "production_api_network_allowed": False,
                           "mapped_api_requests": len(observed), "blocked_requests": blocked,
                           "page_errors": browser_errors,
                           "api_queries": [{"query": x["query"], "status": x["status"], "returned": len(x["ids"])} for x in observed],
                           "preparation": "Foco nativo, edición confirmada con Tab y valor semántico exacto verificados antes de pointerdown; ninguna consulta en preparación; sin reintentos",
                           "measurement": "Desde pointerdown del botón hasta grupo con título y contador visibles y dos animation frames"})
            return result
        except Exception:
            page.screenshot(path=str(OUT / "chrome-diagnostico.png"))
            (OUT / "chrome-semantica.txt").write_text(page.locator("body").aria_snapshot())
            (OUT / "chrome-red.json").write_text(json.dumps({"requests": observed, "blocked": blocked, "page_errors": browser_errors}, indent=2))
            raise
        finally:
            browser.close()


def cleanup():
    guard()
    path = private_state()
    if path.exists():
        state = json.loads(path.read_text())
        compose(state, "down", "--volumes")
        path.unlink()


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"started_utc": datetime.now(timezone.utc).isoformat(), "official_base_sha": BASE,
              "runtime_source_sha": RUNTIME, "api_image": IMAGE, "run_id": os.environ.get("GITHUB_RUN_ID"),
              "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"), "python": platform.python_version(),
              "runner_os": platform.platform(), "runner_cpus": os.cpu_count(), "production_changed": False,
              "network": "Runner a bridge Docker interna, sin puertos publicados ni latencia inyectada; orígenes Chrome/API remapeados al contenedor propio; CDN estático en warm-up",
              "dataset_profile": "1000 filas, 10 grupos de 100, sin fotos ni afiliación declarada; no representa todos los perfiles de datos",
              "execution_complete": False}
    try:
        state = prepare()
        result.update({"orchestration_sha": state["orchestration_sha"], "image_id": state["image_id"],
                       "mysql_digest": state["mysql_digest"]})
        result["dataset"] = seed(state)
        result["resources_before"] = snapshot(state)
        meta = json.loads((ROOT / "deploy/promocion-incremento2.json").read_text())
        result["main_dart_js_sha256"] = hashlib.sha256(request("/app/main.dart.js")[1]).hexdigest()
        require(result["main_dart_js_sha256"] == meta["web_main_sha256"], "Bundle distinto al publicado.")
        result["http"] = http_measure()
        result["browser"] = browser_measure()
        result["resources_after"] = snapshot(state)
        result["dataset_count_after"] = json.loads(compose_exec(state, 'from backend.app.db import transaction\nwith transaction() as c:\n c.execute("SELECT COUNT(*) AS n FROM publicaciones")\n print(__import__("json").dumps(c.fetchone()["n"]))'))
        require(result["dataset_count_after"] == 1000, "Dataset cambió durante el ensayo.")
        result["execution_complete"] = True
        result["public_ec01_outcome"] = "NO CONCLUYENTE: no mide red ni navegador institucional público"
    except Exception as error:
        result["error_type"] = type(error).__name__
        result["error"] = str(error) if isinstance(error, RuntimeError) else "Fallo de ejecución; revisar diagnóstico sintético."
        raise
    finally:
        (OUT / "resultado.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"execution_complete": result["execution_complete"], "http": result.get("http", {}).get("outcome"),
                          "browser": result.get("browser", {}).get("outcome"), "error_type": result.get("error_type")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["run", "cleanup"])
    args = parser.parse_args()
    if args.action == "cleanup":
        cleanup()
    else:
        run()
