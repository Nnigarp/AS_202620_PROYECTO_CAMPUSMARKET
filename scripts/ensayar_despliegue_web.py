"""Prueba nueva del mecanismo de promoción/rollback; solo recursos sintéticos CI.

No compila Flutter, no construye/publica imágenes y no usa Dokploy. La imagen
de control es el mismo Image ID aprobado: esto prueba reemplazo de API y datos,
no compatibilidad con la versión productiva, todavía desconocida.
"""

import argparse
import base64
import hashlib
import json
import os
from datetime import datetime, timezone

from scripts.ensayar_imagen_ghcr import (
    PROBE,
    Trial,
    TrialError,
    require,
    validate_config,
)
from scripts.preparar_despliegue_web import (
    GATES,
    IMAGE,
    IMAGE_ID,
    ROOT,
    SOURCE,
    prepare,
    private_json,
    validate_delta,
    validate_image,
    verify,
)

CHECKS = ("compose", "pull", "backup_restore_synthetic", "preflight", "promote_api_only", "rollback_api_only", "cleanup")


class DeploymentTrial(Trial):
    def backup_restore(self):
        """Sin escritores durante el corte: dump InnoDB y TAR de PNG sintético."""
        dump = self.command(self.compose + ["exec", "-T", "db", "sh", "-ec",
            'MYSQL_PWD="$MYSQL_PASSWORD" mysqldump --single-transaction --no-tablespaces --set-gtid-purged=OFF -u "$MYSQL_USER" "$MYSQL_DATABASE"'], "dump sintético")
        tar = self.command(self.compose + ["exec", "-T", "api", "python", "-c",
            "import base64,io,tarfile; b=io.BytesIO(); t=tarfile.open(fileobj=b,mode='w'); t.add('/app/backend/uploads',arcname='uploads'); t.close(); print(base64.b64encode(b.getvalue()).decode())"], "archivo de imágenes sintéticas")
        dump_file = self.private / "synthetic.sql"
        tar_file = self.private / "synthetic-images.tar"
        for path, data in ((dump_file, dump.encode()), (tar_file, base64.b64decode(tar))):
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
        restore_project = self.project + "-restore"
        restore = self.compose.copy()
        restore[restore.index("--project-name") + 1] = restore_project
        config = json.loads(self.command(restore + ["config", "--format", "json"], "Compose de restauración"))
        validate_config(config, restore_project, self.database)
        label = "label=com.docker.compose.project=" + restore_project
        for kind in (("ps", "-aq"), ("volume", "ls", "-q"), ("network", "ls", "-q")):
            require(not self.command(["docker", *kind, "--filter", label], "aislamiento de restauración").strip(), "Existen recursos previos del proyecto de restauración")
        self.state["restore_started"] = True
        self.save()
        try:
            self.command(restore + ["up", "-d", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180", "db"], "MySQL de restauración", timeout=240)
            self.command(restore + ["exec", "-T", "db", "sh", "-ec", 'MYSQL_PWD="$MYSQL_PASSWORD" mysql -u "$MYSQL_USER" "$MYSQL_DATABASE"'], "restaurar dump sintético", stdin=dump_file.read_text())
            self.command(restore + ["up", "-d", "--no-deps", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180", "api"], "API de restauración", timeout=240)
            self.command(restore + ["exec", "-T", "api", "python", "-c",
                "import base64,io,sys,tarfile; tarfile.open(fileobj=io.BytesIO(base64.b64decode(sys.stdin.read()))).extractall('/app/backend',filter='data')"], "restaurar PNG sintético", stdin=base64.b64encode(tar_file.read_bytes()).decode())
            data = {"mode": "restored", "source_sha": SOURCE, "database": self.database, "fixture": self.state["fixture"]}
            result = json.loads(self.command(restore + ["exec", "-T", "api", "python", "-c", PROBE], "lecturas de restauración", stdin=json.dumps(data)))
            self.checked("backup_restore_synthetic", {**result, "sql_sha256": hashlib.sha256(dump_file.read_bytes()).hexdigest(), "images_sha256": hashlib.sha256(tar_file.read_bytes()).hexdigest(), "production_recovery_verified": False})
        finally:
            self.command(restore + ["down", "--volumes", "--remove-orphans"], "limpiar exclusivamente restauración sintética", timeout=120)
            self.state["restore_started"] = False
            self.save()

    def run(self):
        self.local_docker()
        require(self.state.get("prepared"), "Falta preparación")
        self.config()
        # Contraste real lab -> prod y lab + override -> prod, con el mismo env.
        lab = self.compose.copy()
        lab[-1] = str(ROOT / "deploy/compose.lab.yaml")
        before = json.loads(self.command(lab + ["config", "--format", "json"], "Compose lab"))
        prod = json.loads(self.command(self.compose + ["config", "--format", "json"], "Compose por imagen"))
        overlay = json.loads(self.command(lab + ["-f", str(ROOT / "deploy/compose.web.yaml"), "config", "--format", "json"], "override sin build"))
        validate_delta(before, prod)
        require(overlay == prod, "El override no equivale al Compose por imagen")
        self.begin("pull")
        self.command(["docker", "pull", IMAGE], "descargar digest ya publicado", timeout=240, diagnose_pull=True)
        validate_image(json.loads(self.command(["docker", "image", "inspect", IMAGE], "identidad publicada"))[0])
        self.state["image_id"] = IMAGE_ID
        self.command(["docker", "pull", "mysql:8.4"], "descargar MySQL sintético", timeout=240)
        self.checked("pull", {"reference": IMAGE, "image_id": IMAGE_ID, "rebuilt": False, "republished": False})
        # Control inicial por Image ID, promoción por digest y rollback por ID.
        bootstrap_file = self.private / "control.compose.json"
        private_json(bootstrap_file, {"services": {"api": {"image": IMAGE_ID}}})
        baseline = self.compose + ["-f", str(bootstrap_file)]
        self.command(baseline + ["up", "-d", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "180"], "crear solo el laboratorio sintético", timeout=240)
        self.probe("read")
        self.state["fixture"] = self.probe("seed")
        self.save()
        self.begin("backup_restore_synthetic")
        self.backup_restore()
        archive = self.private / "rollback-image.tar"
        self.command(["docker", "save", IMAGE_ID, "-o", str(archive)], "conservar imagen de control", timeout=120)
        self.command(["docker", "load", "--input", str(archive)], "cargar copia recuperable de control", timeout=120)
        require(json.loads(self.command(["docker", "image", "inspect", IMAGE_ID], "verificar copia recuperada"))[0]["Id"] == IMAGE_ID, "Copia de control distinta")
        with archive.open("rb") as stream:
            archive_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
        evidence = {"scope": "synthetic-ci", "project": self.project, "checked_at": datetime.now(timezone.utc).isoformat(),
                    "gates": {key: {"verified": True, "evidence": "Solo ensayo aislado de este run; sin efecto ni acreditación productiva"} for key in GATES},
                    "rollback": {"image_id": IMAGE_ID, "archive_sha256": archive_sha256}}
        self.begin("preflight")
        plan = prepare(baseline, evidence, self.private / "plan")
        self.checked("preflight", "Plan real; igualdad de Environment, routing, red, volúmenes y cuotas; gates solo sintéticos")
        self.begin("promote_api_only")
        self.command(plan["promote"], "promover solo API sintética", timeout=240)
        promoted = verify(plan, "promoted")
        require(promoted["api"]["container_id"] != plan["baseline"]["api"]["container_id"], "No se reemplazó la API")
        self.probe("restored")
        self.command(self.compose + ["exec", "-T", "api", "python", "-c",
            "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8000/app/'); assert r.status==200; assert b'<base href=\"/app/\">' in r.read()"], "bundle aprobado presente")
        self.checked("promote_api_only", {"db_unchanged": True, "data_and_images_preserved": True, "api_replaced": True})
        self.begin("rollback_api_only")
        self.command(plan["rollback"], "rollback solo API sintética", timeout=240)
        rolled_back = verify(plan, "rollback")
        require(rolled_back["api"]["container_id"] != promoted["api"]["container_id"], "No se reemplazó API durante rollback")
        self.probe("restored")
        self.checked("rollback_api_only", {"db_unchanged": True, "data_and_images_preserved": True, "api_replaced": True,
                                           "control_image_id": IMAGE_ID, "different_version_compatibility_verified": False})

    def cleanup(self):
        try:
            if self.state.get("restore_started"):
                restore = self.compose.copy()
                restore[restore.index("--project-name") + 1] = self.project + "-restore"
                self.local_docker()
                self.command(restore + ["down", "--volumes", "--remove-orphans"], "limpiar restauración del run", timeout=120)
                self.state["restore_started"] = False
                self.save()
        finally:
            super().cleanup()
            for name in ("synthetic.sql", "synthetic-images.tar", "rollback-image.tar"):
                (self.private / name).unlink(missing_ok=True)

    def report(self):
        out = ROOT / "artifacts/despliegue-web-seguro"
        out.mkdir(parents=True, exist_ok=True)
        self.state["production_deployment_blocked"] = True
        self.state["production_recovery_verified"] = False
        self.state["rollback_control_uses_same_image"] = True
        self.state["passed"] = all(self.state["checks"].get(key, {}).get("status") == "CUMPLE" for key in CHECKS) and not self.state.get("failure")
        (out / "resultado.json").write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        require(self.state["passed"], "Ensayo del mecanismo incompleto; consultar resultado.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "run", "cleanup", "report"))
    args = parser.parse_args()
    trial = DeploymentTrial()
    try:
        getattr(trial, args.phase)()
    except (TrialError, RuntimeError, OSError, ValueError, LookupError, TypeError) as error:
        message = str(error) if isinstance(error, (TrialError, RuntimeError)) else type(error).__name__
        trial.state.setdefault("failure", args.phase + ": " + message)
        trial.save()
        print("FAIL " + trial.state["failure"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
