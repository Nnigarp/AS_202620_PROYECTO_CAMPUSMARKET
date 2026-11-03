"""Cliente del ensayo, ejecutado por stdin dentro de la API efímera de CI."""

import hashlib
import json
import re
import secrets
import sys
from io import BytesIO
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image

BASE = "http://127.0.0.1:8000"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    content = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True).encode()
    return hashlib.sha256(content).hexdigest()


def request(method, path, status=200, *, user=None, payload=None, body=None, content_type=None):
    headers = {"Authorization": "Bearer " + user["token"]} if user else {}
    if payload is not None:
        body = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    if content_type:
        headers["Content-Type"] = content_type
    req = Request(BASE + path, data=body, headers=headers, method=method)
    try:
        response = urlopen(req, timeout=20)
    except HTTPError as error:
        response = error
    with response:
        require(response.status == status, f"{method} {path}: esperado {status}, observado {response.status}")
        raw = response.read()
        data = json.loads(raw) if raw and "application/json" in response.headers.get("Content-Type", "") else raw
        return data, response.headers


def login(user):
    data, _ = request("POST", "/usuarios/login", payload={"correo": user["correo"], "password": user["password"]})
    user["token"] = data["access_token"]


def shared(state, revision):
    health, headers = request("GET", "/health")
    require(health["status"] == "ok" and headers.get("X-CampusMarket-Revision") == revision, "Salud/revisión incorrecta")
    pub, _ = request("GET", f'/catalogo/{state["publicacion_id"]}')
    require(pub["propietario_id"] == state["users"]["a"]["id"] and pub["precio"] == 65.5, "Publicación heredada alterada")
    require(pub["universidad_id"] == 1, "Institución histórica alterada")
    photo, _ = request("GET", state["photo_url"])
    require(digest(photo) == state["photo_sha256"], "Fotografía alterada")
    me, _ = request("GET", "/usuarios/me", user=state["users"]["b"])
    require(me["id"] == state["users"]["b"]["id"], "Sesión/usuario perdido")


def run(phase, state, revision):
    require(re.fullmatch(r"cm-i2-[0-9]+-[0-9]+", state["project"]), "Solo se admite el proyecto sintético de CI")
    require(re.fullmatch(r"[0-9a-f]{40}", revision), "Revisión inválida")
    checks = []
    if phase == "seed":
        users = {}
        for key in "abc":
            user = {"correo": f"{key}-{secrets.token_hex(8)}@campus.test", "password": secrets.token_urlsafe(24)}
            created, _ = request("POST", "/usuarios/registro", 201, payload={
                **user, "nombre": f"Ensayo {key}", "universidad_id": 1 if key == "a" else None,
            })
            user["id"] = created["id"]
            login(user)
            users[key] = user
        state["users"] = users
        pub, _ = request("POST", "/publicaciones", 201, user=users["a"], payload={
            "titulo": "Libro sintético previo", "descripcion": "Fixture anterior a la migración del incremento",
            "precio": 65.5, "modalidad": "venta", "estado": "usado",
        })
        state["publicacion_id"] = pub["id"]
        png = BytesIO()
        Image.new("RGB", (32, 24), "purple").save(png, format="PNG")
        boundary = "cm-" + secrets.token_hex(12)
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="archivo"; filename="ensayo.png"\r\n'
                'Content-Type: image/png\r\n\r\n').encode() + png.getvalue() + f"\r\n--{boundary}--\r\n".encode()
        image, _ = request("POST", f'/publicaciones/{pub["id"]}/imagenes', 201, user=users["a"],
                           body=body, content_type=f"multipart/form-data; boundary={boundary}")
        state["photo_url"] = image["imagen_url"]
        state["photo_sha256"] = digest(request("GET", image["imagen_url"])[0])
        state["old_contract_sha256"] = digest(request("GET", "/openapi.json")[0])
        shared(state, revision)
        checks.append("imagen-previa-crea-usuarios-publicacion-foto-sinteticos")
    else:
        shared(state, revision)
        checks.append("publicacion-foto-y-sesion-conservadas")
    if phase == "upgrade":
        a, b, c = (state["users"][k] for k in "abc")
        pid = state["publicacion_id"]
        request("GET", "/favoritos", 401)
        for _ in range(2):
            request("PUT", f"/favoritos/{pid}", 204, user=b)
        favorites, headers = request("GET", "/favoritos", user=b)
        require(len(favorites) == 1 and favorites[0]["id"] == pid, "Favorito duplicado/perdido")
        require(headers.get("Cache-Control") == "no-store", "Favoritos permiten caché")
        require(request("GET", f'/favoritos?usuario_id={b["id"]}', user=c)[0] == [], "Favoritos ajenos expuestos")
        request("DELETE", f"/favoritos/{pid}", 204, user=c)
        require(len(request("GET", "/favoritos", user=b)[0]) == 1, "Borrado ajeno alteró favorito")
        checks.append("favoritos-privados-idempotentes-en-mysql")
        conversation, _ = request("POST", "/conversaciones", user=b, payload={"publicacion_id": pid})
        cid = conversation["id"]
        same, _ = request("POST", "/conversaciones", user=b, payload={"publicacion_id": pid})
        require(same["id"] == cid, "Conversación duplicada")
        state["conversacion_id"] = cid
        request("POST", "/conversaciones", 409, user=a, payload={"publicacion_id": pid})
        path = f"/conversaciones/{cid}/mensajes"
        request("GET", f"/conversaciones/{cid}", 404, user=c)
        request("GET", path, 404, user=c)
        body = {"texto": "Consulta sintética del comprador", "clave": secrets.token_hex(16)}
        request("POST", path, 404, user=c, payload=body)
        first, _ = request("POST", path, 201, user=b, payload=body)
        repeated, _ = request("POST", path, 201, user=b, payload=body)
        require(first["id"] == repeated["id"] and first["remitente_id"] == b["id"], "Mensaje duplicado o suplantado")
        request("POST", path, 409, user=b, payload={**body, "texto": "Otro contenido"})
        request("POST", path, 422, user=b, payload={**body, "remitente_id": a["id"]})
        request("POST", path, 201, user=a, payload={"texto": "Respuesta sintética del vendedor", "clave": secrets.token_hex(16)})
        require(len(request("GET", path, user=b)[0]["mensajes"]) == 2, "Historia de mensajes incorrecta")
        require(len(request("GET", "/conversaciones", user=a)[0]) == 1, "Bandeja vendedor incorrecta")
        require(request("GET", "/conversaciones", user=c)[0] == [], "Bandeja ajena expuesta")
        checks.append("chat-bandejas-participantes-e-idempotencia")
        request("PATCH", "/usuarios/me", user=a, payload={"nombre": "Ensayo a", "universidad_id": 2})
        detail, _ = request("GET", f"/catalogo/{pid}")
        require(detail["universidad"]["sigla"] == "UTB", "Universidad atribuida desde perfil actual")
        legacy, _ = request("POST", "/publicaciones", 201, user=b, payload={
            "titulo": "Sin institución", "descripcion": "Fixture sin institución declarada al publicar",
            "precio": 10, "modalidad": "alquiler", "estado": "usado",
        })
        request("PATCH", "/usuarios/me", user=b, payload={"nombre": "Ensayo b", "universidad_id": 2})
        require(request("GET", f'/catalogo/{legacy["id"]}')[0]["universidad"] is None, "Universidad inventada para heredada")
        request("PUT", f'/favoritos/{legacy["id"]}', 204, user=b)
        request("DELETE", f'/publicaciones/{legacy["id"]}', 204, user=b)
        require([v["id"] for v in request("GET", "/favoritos", user=b)[0]] == [pid], "Eliminada aparece en favoritos")
        checks.append("universidad-snapshot-null-y-eliminadas")
        previous = dict(b)
        request("POST", "/usuarios/logout", 204, user=b)
        request("GET", "/favoritos", 401, user=previous)
        login(b)
        checks.append("logout-revoca-sesion-sin-borrar-datos")
    if phase in {"upgrade", "persist"}:
        b = state["users"]["b"]
        require(len(request("GET", "/favoritos", user=b)[0]) == 1, "Favoritos no persistieron")
        require(len(request("GET", f'/conversaciones/{state["conversacion_id"]}/mensajes', user=b)[0]["mensajes"]) == 2,
                "Mensajes no persistieron")
        html, _ = request("GET", "/app/")
        require(b'<base href="/app/">' in html, "Base href incorrecto")
        for asset in ("/app/flutter_bootstrap.js", "/app/main.dart.js", "/docs"):
            content = request("GET", asset)[0]
            require(len(content) > 100, "Asset/documentación ausente")
            if asset == "/app/main.dart.js":
                require(digest(content) == state["candidate_web_main_sha256"], "Bundle servido distinto al compilado")
        request("GET", "/app/inexistente.js", 404)
        actual, _ = request("GET", "/openapi.json")
        require(digest(actual) == state["candidate_contract_sha256"], "OpenAPI de imagen no coincide con contrato")
        checks.append("persistencia-web-assets-y-contrato-exacto")
    if phase == "rollback":
        require(digest(request("GET", "/openapi.json")[0]) == state["old_contract_sha256"], "Rollback no recuperó contrato previo")
        checks.append("rollback-api-previa-compatible-con-datos-ampliados")
    return {"state": state, "checks": checks}


if __name__ == "__main__":
    data = json.load(sys.stdin)
    try:
        print(json.dumps(run(data["phase"], data["state"], data["revision"])))
    except (AssertionError, KeyError, ValueError, OSError) as error:
        detail = str(error)
        for user in data.get("state", {}).get("users", {}).values():
            for key in ("password", "token"):
                if user.get(key):
                    detail = detail.replace(user[key], "<redacted>")
        print(json.dumps({"error": type(error).__name__, "detail": detail[:400]}))
        raise SystemExit(1) from None
