"""Candidato Pages sin publicar: solo lecturas públicas y servidor estático local."""

import argparse
import functools
import hashlib
import http.server
import json
import os
import re
import shutil
import subprocess
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from scripts.verificar_web_institucional import Chrome

SOURCE = "fd7a3cc3903c773330cfa6ba9345872932f9000b"
REPOSITORY = "Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET"
API = "https://campusmarket.iscoutb.dev"
ORIGIN = "https://nnigarp.github.io"
BASE_HREF = "/AS_202620_PROYECTO_CAMPUSMARKET/"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/pages-candidate"
SITE = OUT / "site"


class Rejected(RuntimeError):
    pass


def require(value, message):
    if not value:
        raise Rejected(message)


def api_path(method, path):
    require(method in {"GET", "HEAD", "OPTIONS"}, "El ensayo no permite escrituras HTTP")
    paths = r"/(?:health|docs|openapi\.json|catalogo(?:/[0-9]+)?|uploads/publicaciones/[0-9]+/[a-zA-Z0-9._-]+)"
    allowed = bool(re.fullmatch(paths, path))
    if method == "OPTIONS":
        allowed = path in {"/catalogo", "/usuarios/login", "/publicaciones"}
    require(allowed, "Ruta pública fuera del alcance de lectura")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def fetch(method, path, origin=ORIGIN, extra=None):
    api_path(method, path)
    request = urllib.request.Request(API + path, method=method, headers={"Origin": origin, **(extra or {})})
    opener = urllib.request.build_opener(NoRedirect())
    try:
        response = opener.open(request, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.read(10 * 1024 * 1024), response.headers


def validate_bundle(site):
    require((site / "index.html").is_file() and (site / "main.dart.js").is_file(), "Bundle incompleto")
    require('<base href="' + BASE_HREF + '">' in (site / "index.html").read_text(), "Base href incorrecto para Pages")
    require(API in (site / "main.dart.js").read_text(), "API pública no incorporada al bundle")
    for path in site.rglob("*"):
        require(not path.is_symlink(), "El bundle no admite symlinks")
        require(path.name not in {".git", ".env", "CNAME"}, "Archivo privado o cambio de dominio en bundle")
        require(path.suffix not in {".map", ".pem", ".key", ".sql", ".db", ".sqlite"}, "Archivo no publicable en bundle")


def file_manifest(site):
    return {path.relative_to(site).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(site.rglob("*")) if path.is_file()}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def preflight(record, private):
    checks = []
    record["public_read_checks"] = checks
    for path in ("/health", "/docs", "/openapi.json", "/catalogo"):
        status, raw, headers = fetch("GET", path)
        allowed = headers.get("Access-Control-Allow-Origin")
        checks.append({"method": "GET", "path": path, "status": status, "allow_origin": allowed,
                       "server": headers.get("Server"), "content_type": headers.get("Content-Type")})
        require(status == 200, "HTTP público no válido: " + path + "; status=" + str(status))
        require(allowed == ORIGIN, "CORS público no válido: " + path + "; allow_origin=" + str(allowed))
        if path == "/health":
            require(json.loads(raw).get("status") == "ok", "API no saludable")
        if path == "/catalogo":
            catalog = json.loads(raw)
    for path, method in (("/catalogo", "GET"), ("/usuarios/login", "POST"), ("/publicaciones", "POST")):
        status, _, headers = fetch("OPTIONS", path, extra={"Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "content-type,authorization,idempotency-key"})
        require(status == 200 and headers.get("Access-Control-Allow-Origin") == ORIGIN, "Preflight CORS rechazado: " + path)
        require(headers.get("Access-Control-Allow-Credentials") == "true", "CORS credentials inesperado")
        checks.append({"method": "OPTIONS", "path": path, "status": status, "allow_origin": ORIGIN})
    status, _, headers = fetch("GET", "/health", origin="http://127.0.0.1:8080")
    require(status == 200 and headers.get("Access-Control-Allow-Origin") == "http://127.0.0.1:8080", "Origen de ensayo Chrome no permitido por CORS actual")
    status, _, headers = fetch("OPTIONS", "/catalogo", origin="https://pages-rejected.invalid", extra={"Access-Control-Request-Method": "GET"})
    require(status == 400 and headers.get("Access-Control-Allow-Origin") is None, "CORS permite un origen no autorizado")
    # Sin semilla ni registro en producción: se usa una oferta ya pública.
    item = next((item for item in catalog if item.get("imagenes")), None)
    require(item is not None, "Falta muestra pública con imagen para comprobar detalle sin escribir datos")
    path = "/catalogo/" + str(int(item["id"]))
    status, raw, _ = fetch("GET", path)
    require(status == 200 and json.loads(raw)["id"] == item["id"], "Detalle público no disponible")
    principal = next((image for image in item["imagenes"] if image.get("es_principal")), item["imagenes"][0])
    image = urllib.parse.urlsplit(urllib.parse.urljoin(API, principal["imagen_url"]))
    require(image.scheme == "https" and image.netloc == urllib.parse.urlsplit(API).netloc and not image.query, "Imagen fuera de HTTPS/API esperada")
    status, raw, _ = fetch("GET", image.path)
    require(status == 200 and bool(raw), "Imagen pública no disponible")
    private.write_text(json.dumps({"id": item["id"], "title": item["titulo"], "image_path": image.path}))
    private.chmod(0o600)
    record["public_read_checks"] = checks
    record["cors_denied_origin_rejected"] = True
    record["public_detail_and_image"] = True
    record["public_bodies_archived"] = False


def verify(record, private):
    source = ROOT / "source/frontend/campusmarket/build/web"
    validate_bundle(source)
    shutil.copytree(source, SITE)
    (SITE / ".nojekyll").touch()
    (SITE / "source-revision.txt").write_text(SOURCE + "\n")
    before = file_manifest(SITE)
    stage = Path(os.environ["RUNNER_TEMP"]) / ("pages-preview-" + os.environ["GITHUB_RUN_ID"])
    stage.mkdir()
    shutil.copytree(SITE, stage / BASE_HREF.strip("/"))
    handler = functools.partial(QuietHandler, directory=str(stage))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 8080), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    chrome = None
    try:
        chrome = Chrome()
        chrome.cdp("Network.enable")
        chrome.cdp("Network.setBlockedURLs", {"urls": [API + "/usuarios/*", API + "/publicaciones*", API + "/administracion/*"]})
        fixture = json.loads(private.read_text())
        chrome.call("POST", "/url", {"url": "http://127.0.0.1:8080" + BASE_HREF})
        chrome.wait_text("Catálogo")
        chrome.click_text("Catálogo")
        chrome.wait_text(fixture["title"])
        chrome.click_text(fixture["title"])
        chrome.wait_text("Detalle de publicación")
        chrome.wait_text("Descripción")
        chrome.call("POST", "/back", {})
        chrome.wait_text("Catálogo")
        chrome.call("POST", "/refresh", {})
        chrome.wait_text("Catálogo")
        events = [json.loads(item["message"])["message"] for item in chrome.call("POST", "/log", {"type": "performance"})]
        requests = [event["params"]["request"] for event in events if event["method"] == "Network.requestWillBeSent"]
        public = [r for r in requests if r["url"].startswith(API + "/")]
        require(public and all(r["method"] in {"GET", "HEAD", "OPTIONS"} for r in public), "Escritura o ausencia de tráfico API en navegador")
        require(not any("/catalogo" in r["url"] and not r["url"].startswith(API + "/catalogo") for r in requests), "Catálogo dirigido al origen Pages")
        responses = [event["params"]["response"] for event in events if event["method"] == "Network.responseReceived"]
        api_responses = [{"path": urllib.parse.urlsplit(r["url"]).path, "status": r["status"]} for r in responses if r["url"].startswith(API + "/")]
        for expected in ("/catalogo", "/catalogo/" + str(fixture["id"]), fixture["image_path"]):
            require(any(r["path"] == expected and r["status"] == 200 for r in api_responses), "Lectura real no acreditada en navegador: " + expected)
        assets = [r for r in responses if r["url"].startswith("http://127.0.0.1:8080" + BASE_HREF)]
        require(any("main.dart.js" in r["url"] for r in assets) and all(r["status"] < 400 for r in assets), "Assets Pages ausentes o fallidos")
        require(not any(r["url"].startswith("http://") and not r["url"].startswith("http://127.0.0.1:8080/") for r in requests), "Recurso externo HTTP no permitido")
        errors = chrome.call("POST", "/log", {"type": "browser"})
        require(not any(e["level"] == "SEVERE" for e in errors), "Error JavaScript/CORS del navegador")
        record["browser"] = {"inicio_catalogo_detalle_atras_recarga": True, "api_reads": api_responses,
                             "assets_received": len(assets), "write_endpoints_blocked": True,
                             "origin": "http://127.0.0.1:8080", "pages_https_acceptance_pending": True}
    finally:
        if chrome:
            chrome.call("DELETE", "")
        server.shutdown()
        server.server_close()
        shutil.rmtree(stage)
    require(file_manifest(SITE) == before, "Bundle cambió durante el ensayo")
    result = subprocess.run([os.environ["PAGES_GITLEAKS"], "dir", str(SITE), "--no-banner", "--redact"], capture_output=True, text=True, check=False)
    require(result.returncode == 0, "Scanner detectó secretos o no completó el análisis")
    record["secret_scan"] = {"gitleaks": "8.30.1", "exit_code": 0}
    record["bundle_manifest_sha256"] = hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
    (OUT / "files.sha256.json").write_text(json.dumps(before, indent=2) + "\n")
    record["passed"] = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("preflight", "verify"))
    phase = parser.parse_args().phase
    require(os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("RUNNER_ENVIRONMENT") == "github-hosted", "Solo runner efímero GitHub")
    require(os.getenv("GITHUB_REPOSITORY") == REPOSITORY, "Solo fork autorizado")
    OUT.mkdir(parents=True, exist_ok=True)
    record_file = OUT / "result.json"
    private = Path(os.environ["RUNNER_TEMP"]) / "pages-public-sample.json"
    record = json.loads(record_file.read_text()) if record_file.exists() else {
        "workflow_sha": os.environ["GITHUB_SHA"], "source_sha": SOURCE, "api": API, "base_href": BASE_HREF,
        "pages_origin": ORIGIN, "run": "https://github.com/" + REPOSITORY + "/actions/runs/" + os.environ["GITHUB_RUN_ID"],
        "published": False, "ghcr_changed": False, "passed": False}
    try:
        if phase == "preflight":
            preflight(record, private)
        else:
            verify(record, private)
    except (OSError, ValueError, LookupError, RuntimeError) as error:
        record["failure"] = str(error) if isinstance(error, Rejected) else type(error).__name__
        print("FAIL " + record["failure"])
        return 1
    finally:
        record_file.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        if phase == "verify":
            private.unlink(missing_ok=True)
    print("PASS " + phase)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
