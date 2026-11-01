"""Prepara tres ramas auxiliares y un bundle recuperable; nunca escribe gh-pages.

Sin Flutter, Docker, deploy, cambios de Pages ni peticiones HTTP de escritura.
Las únicas escrituras remotas permitidas son las tres referencias STAGING.
"""

import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path

REPOSITORY = "Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET"
WORK_BRANCH = "ops/ensayo-pages-api-publica-20261031"
RUN = 41253225664
ARTIFACT = 13062186958
WORKFLOW_SHA = "21842586551f470929ce8c19100f1cc7ea5eff34"
SOURCE_SHA = "fd7a3cc3903c773330cfa6ba9345872932f9000b"
ZIP_SHA = "982ee6df36ad821ab6ae6410e3eefee0b516d06a7cac934a1da730cb14095fad"
MANIFEST_SHA = "f401ea11654cc26185959c69bffa6db783a8698a1d77c87ddf5cdd03a42e2ebd"
OLD = "4626e11beb259faea25e64647ec89dd1b54a9246"
OLD_TREE = "cc4186f6b5b997336e9b98b1beef2927bd829e4a"
URL = "https://nnigarp.github.io/AS_202620_PROYECTO_CAMPUSMARKET/"
PUBLISH_BRANCH = "gh-pages"
BACKUP = "backup/pages-4626e11beb25-20261031"
CANDIDATE = "staging/pages-41253225664"
ROLLBACK = "staging/pages-rollback-41253225664"
STAGING = {BACKUP, CANDIDATE, ROLLBACK}
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/preparacion-pages"


class Blocked(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Blocked(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def command(args, stdin=None, env=None, allowed=(0,)):
    result = subprocess.run(args, input=stdin, capture_output=True, env=env, check=False, timeout=180)
    require(result.returncode in allowed, "Comando rechazado: " + args[0] + "; exit=" + str(result.returncode) + "; salida privada omitida")
    return result.stdout


def git(*args, stdin=None, env=None, allowed=(0,)):
    return command(["git", *args], stdin=stdin, env=env, allowed=allowed).decode().strip()


def api(path):
    allowed = {"pages", "actions/runs/" + str(RUN), "actions/artifacts/" + str(ARTIFACT)}
    require(path in allowed, "Lectura API no permitida")
    return json.loads(command(["gh", "api", "repos/" + REPOSITORY + "/" + path]))


def validate_metadata(run, artifact):
    require(run["id"] == RUN and run["head_sha"] == WORKFLOW_SHA, "Run/fuente de ensayo distintos")
    require(run["repository"]["full_name"] == REPOSITORY and run["head_repository"]["full_name"] == REPOSITORY, "Repositorio de origen distinto")
    require(run["event"] == "push" and run["head_branch"] == WORK_BRANCH and run["path"] == ".github/workflows/ensayo-pages.yml", "Workflow/evento/rama distintos")
    require(run["status"] == "completed" and run["conclusion"] == "success", "Run no aprobado")
    require(artifact["id"] == ARTIFACT and artifact["name"] == f"pages-candidate-{RUN}-1" and artifact["expired"] is False, "Artefacto ausente o caducado")
    require(artifact["workflow_run"]["id"] == RUN and artifact["workflow_run"]["head_sha"] == WORKFLOW_SHA, "Artefacto de otro run")
    require(artifact["digest"] == "sha256:" + ZIP_SHA, "Hash GitHub distinto del ZIP aprobado")


def validate_pages(data):
    require(data.get("build_type") == "legacy" and data.get("source") == {"branch": PUBLISH_BRANCH, "path": "/"}, "Pages no usa gh-pages/root: detener sin cambiar Settings")
    require(data.get("html_url") == URL and data.get("https_enforced") is True and not data.get("cname"), "URL/HTTPS/dominio distintos del alcance autorizado")
    return {key: data.get(key) for key in ("build_type", "source", "html_url", "https_enforced", "cname")}


def safe_path(name):
    require(isinstance(name, str) and bool(re.fullmatch(r"[A-Za-z0-9_./-]+", name)), "Ruta de bundle inválida")
    require(not name.startswith("/") and all(part not in {"", ".", ".."} for part in name.split("/")), "Ruta fuera del bundle")
    require(name != "CNAME" and not any(part.startswith(".env") or part == ".git" for part in name.split("/")), "Archivo de configuración/secretos no permitido")


def verify_zip(path):
    require(digest(path.read_bytes()) == ZIP_SHA, "ZIP original modificado")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "ZIP con entradas duplicadas")
        require(sum(info.file_size for info in archive.infolist()) <= 128 * 1024 * 1024, "ZIP excede el tamaño esperado")
        for info in archive.infolist():
            require(stat.S_IFMT(info.external_attr >> 16) in {0, stat.S_IFREG}, "ZIP con enlaces o entradas no regulares")
        manifest = json.loads(archive.read("files.sha256.json"))
        require(len(manifest) == 42 and digest(json.dumps(manifest, sort_keys=True).encode()) == MANIFEST_SHA, "Manifiesto de otro bundle")
        require(set(names) == {"site/" + name for name in manifest} | {"result.json", "files.sha256.json"}, "ZIP con archivos faltantes o adicionales")
        files = {}
        for name, expected in manifest.items():
            safe_path(name)
            data = archive.read("site/" + name)
            require(digest(data) == expected, "Archivo no corresponde al bundle aprobado")
            files[name] = data
        result = json.loads(archive.read("result.json"))
        require(result.get("passed") is True and result.get("published") is False and not result.get("failure"), "Evidencia del candidato incompleta")
        require(result["workflow_sha"] == WORKFLOW_SHA and result["source_sha"] == SOURCE_SHA and result["run"] == f"https://github.com/{REPOSITORY}/actions/runs/{RUN}", "Procedencia interna distinta")
        require(result["secret_scan"] == {"gitleaks": "8.30.1", "exit_code": 0}, "Escaneo previo no acreditado")
        require(result["bundle_manifest_sha256"] == MANIFEST_SHA and result["base_href"] == "/AS_202620_PROYECTO_CAMPUSMARKET/" and result["api"] == "https://campusmarket.iscoutb.dev", "Destino del bundle distinto")
        require(files[".nojekyll"] == b"" and files["source-revision.txt"].decode().strip() == SOURCE_SHA, "Marcadores Pages distintos")
        return files, manifest


def read_tree(ref):
    files = {}
    entries = command(["git", "ls-tree", "-rz", ref]).split(b"\0")
    for entry in filter(None, entries):
        metadata, path = entry.split(b"\t", 1)
        mode, kind, blob = metadata.decode().split()
        require(mode == "100644" and kind == "blob", "Árbol con enlaces o modos no aprobados")
        files[path.decode()] = command(["git", "cat-file", "blob", blob])
    return files


def tree_manifest(files):
    return {name: digest(data) for name, data in sorted(files.items())}


def write_tree(files, index_path):
    env = {**os.environ, "GIT_INDEX_FILE": str(index_path)}
    git("read-tree", "--empty", env=env)
    for name, content in sorted(files.items()):
        safe_path(name)
        blob = git("hash-object", "-w", "--stdin", stdin=content)
        git("update-index", "--add", "--cacheinfo", "100644," + blob + "," + name, env=env)
    return git("write-tree", env=env)


def create_commit(tree, parent, message):
    return git("-c", "user.name=github-actions[bot]", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
               "commit-tree", tree, "-p", parent, stdin=(message + "\n").encode())


def remote_head(branch):
    require(branch in STAGING | {PUBLISH_BRANCH}, "Referencia fuera de alcance")
    raw = git("ls-remote", "origin", "refs/heads/" + branch)
    if not raw:
        return None
    require(len(raw.splitlines()) == 1, "Referencia remota ambigua")
    sha, ref = raw.split()
    require(ref == "refs/heads/" + branch and re.fullmatch(r"[0-9a-f]{40}", sha), "Referencia remota inválida")
    return sha


def staged_commit(branch, tree, parent, message):
    require(branch in {CANDIDATE, ROLLBACK}, "Solo ramas auxiliares de preparación")
    sha = remote_head(branch)
    if sha:
        git("fetch", "origin", "refs/heads/" + branch)
        require(git("rev-parse", sha + "^{tree}") == tree and git("show", "-s", "--format=%P", sha) == parent, "Rama auxiliar existente con contenido o padre distintos")
        return sha
    return create_commit(tree, parent, message)


def push_staging(refs):
    require(set(refs) == STAGING and PUBLISH_BRANCH not in refs, "Push fuera de ramas auxiliares")
    require(remote_head(PUBLISH_BRANCH) == OLD, "gh-pages cambió: detener antes de preparar")
    backup = remote_head(BACKUP)
    require(backup in {None, OLD}, "Referencia de respaldo ya ocupada")
    for branch, sha in refs.items():
        require(re.fullmatch(r"[0-9a-f]{40}", sha), "Commit auxiliar inválido")
        git("update-ref", "refs/heads/" + branch, sha)  # Solo el repo efímero.
    git("push", "--atomic", "origin", *[sha + ":refs/heads/" + branch for branch, sha in sorted(refs.items())])
    require(remote_head(PUBLISH_BRANCH) == OLD, "Cambio concurrente de publicación; no se autoriza promover")
    require(all(remote_head(branch) == sha for branch, sha in refs.items()), "No se acreditaron todas las ramas auxiliares")


def main():
    record = {"published": False, "gh_pages_modified": False, "passed": False}
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        require(os.getenv("GITHUB_REPOSITORY") == REPOSITORY and os.getenv("GITHUB_REF") == "refs/heads/" + WORK_BRANCH, "Solo rama autorizada del fork")
        require(os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("RUNNER_ENVIRONMENT") == "github-hosted", "Solo runner efímero GitHub")
        require(os.getenv("GITHUB_EVENT_NAME") in {"push", "workflow_dispatch"}, "Evento no autorizado")
        require(git("remote", "get-url", "origin").removesuffix(".git") == "https://github.com/" + REPOSITORY, "Remote distinto del fork")
        pages = validate_pages(api("pages"))
        run, artifact = api("actions/runs/" + str(RUN)), api("actions/artifacts/" + str(ARTIFACT))
        validate_metadata(run, artifact)
        require(remote_head(PUBLISH_BRANCH) == OLD, "Cambió la versión pública desde la inspección")
        git("fetch", "origin", "refs/heads/" + PUBLISH_BRANCH)
        require(git("rev-parse", OLD + "^{tree}") == OLD_TREE, "Árbol anterior no corresponde a la inspección")
        old_files = read_tree(OLD)
        require(len(old_files) == 41 and not ({"CNAME", "404.html", "robots.txt", "README.md"} & old_files.keys()), "Contenido anterior distinto: requiere nueva revisión")
        with tempfile.TemporaryDirectory(prefix="pages-promocion-", dir=os.environ["RUNNER_TEMP"]) as directory:
            private = Path(directory)
            original = private / "original.zip"
            with original.open("wb") as output:
                result = subprocess.run(["gh", "api", f"repos/{REPOSITORY}/actions/artifacts/{ARTIFACT}/zip"], stdout=output, stderr=subprocess.PIPE, check=False, timeout=180)
            require(result.returncode == 0, "No se pudo recuperar el artefacto original de Actions; no usar otro build")
            files, manifest = verify_zip(original)
            tree = write_tree(files, private / "candidate.index")
            require(tree_manifest(read_tree(tree)) == manifest, "Árbol Git distinto del artefacto aprobado")
            candidate = staged_commit(CANDIDATE, tree, OLD, f"Prepare Pages artifact {ARTIFACT}; ZIP sha256:{ZIP_SHA}; source {SOURCE_SHA}")
            rollback = staged_commit(ROLLBACK, OLD_TREE, candidate, "Prepare Pages rollback to " + OLD)
            require(git("rev-parse", rollback + "^{tree}") == OLD_TREE and tree_manifest(read_tree(rollback)) == tree_manifest(old_files), "Rollback no restaura los mismos bytes")
            refs = {BACKUP: OLD, CANDIDATE: candidate, ROLLBACK: rollback}
            push_staging(refs)
            bundle = OUT / "pages-preparacion.bundle"
            git("bundle", "create", str(bundle), *["refs/heads/" + branch for branch in sorted(refs)])
            git("bundle", "verify", str(bundle))
            recovery = private / "recovery.git"
            git("init", "--bare", str(recovery))
            git("--git-dir=" + str(recovery), "fetch", str(bundle), *["refs/heads/" + b + ":refs/heads/" + b for b in sorted(refs)])
            require(all(git("--git-dir=" + str(recovery), "rev-parse", "refs/heads/" + b) == sha for b, sha in refs.items()), "Bundle no recupera las referencias preparadas")
            require(validate_pages(api("pages")) == pages and remote_head(PUBLISH_BRANCH) == OLD, "Pages cambió durante la preparación")
            old_manifest = tree_manifest(old_files)
            record.update({"passed": True, "artifact": ARTIFACT, "run_original": RUN, "zip_sha256": ZIP_SHA,
                           "manifest_sha256": MANIFEST_SHA, "source_sha": SOURCE_SHA, "workflow_sha": os.environ["GITHUB_SHA"],
                           "pages": pages, "old_sha": OLD, "old_tree": OLD_TREE, "candidate_sha": candidate,
                           "candidate_tree": tree, "rollback_sha": rollback, "rollback_tree": OLD_TREE,
                           "staging_refs": refs, "candidate_files": len(files), "old_files": len(old_files),
                           "added": sorted(files.keys() - old_files.keys()), "removed": sorted(old_files.keys() - files.keys()),
                           "changed": sorted(n for n in files.keys() & old_files.keys() if files[n] != old_files[n]),
                           "unchanged": sum(files[n] == old_files[n] for n in files.keys() & old_files.keys()),
                           "bundle_sha256": digest(bundle.read_bytes()), "bundle_restore_verified": True,
                           "publication_requires_explicit_authorization": True})
            (OUT / "previous-files.sha256.json").write_text(json.dumps(old_manifest, indent=2) + "\n")
            (OUT / "candidate-files.sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print("PASS preparación: ramas auxiliares y recuperación verificadas; gh-pages intacta")
    except (Blocked, OSError, ValueError, LookupError, subprocess.SubprocessError) as error:
        record["failure"] = str(error) if isinstance(error, Blocked) else type(error).__name__
        print("FAIL " + record["failure"])
        return 1
    finally:
        (OUT / "plan.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
