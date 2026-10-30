"""Regresiones del preflight: Compose real con env sintético, sin daemon ni datos."""

import copy
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.preparar_despliegue_web import (
    GATES,
    IMAGE,
    IMAGE_ID,
    PROJECT,
    ROOT,
    SOURCE,
    UP_API,
    Blocked,
    command,
    prepare,
    snapshot,
    validate_attestations,
    validate_delta,
    validate_image,
    verify,
)


class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        binary = os.environ.get("CAMPUSMARKET_COMPOSE_TEST_BIN")
        compose = [binary] if binary else ["docker", "compose"]
        if not binary and not shutil.which("docker"):
            raise RuntimeError("Se requiere Docker Compose real; no se acepta omitir estas pruebas")
        with tempfile.TemporaryDirectory() as temp:
            env = Path(temp) / "synthetic.env"
            env.write_text("MYSQL_PASSWORD=SYNTHETIC_PRIVATE_SENTINEL\nMYSQL_ROOT_PASSWORD=SYNTHETIC_ROOT\nMYSQL_DATABASE=preflight_test\nCAMPUSMARKET_REVISION=" + "a" * 40 + "\n")
            prefix = compose + ["--project-name", PROJECT, "--env-file", str(env)]

            def config(files):
                parts = prefix.copy()
                for name in files:
                    parts += ["-f", str(ROOT / "deploy" / name)]
                result = subprocess.run(parts + ["config", "--format", "json"], text=True, capture_output=True, check=False)
                if result.returncode:
                    raise RuntimeError("Docker Compose no validó el archivo; salida privada omitida")
                return json.loads(result.stdout)

            cls.lab = config(["compose.lab.yaml"])
            cls.prod = config(["compose.prod.yaml"])
            cls.overlay = config(["compose.lab.yaml", "compose.web.yaml"])

    def evidence(self):
        return {"checked_at": datetime.now(timezone.utc).isoformat(), "scope": "production", "project": PROJECT,
                "gates": {key: {"verified": True, "evidence": "Referencia sintética de unittest"} for key in GATES},
                "rollback": {"image_id": "sha256:" + "0" * 64, "archive_sha256": "1" * 64}}

    def image(self):
        return {"Id": IMAGE_ID, "RepoDigests": [IMAGE], "Os": "linux", "Architecture": "amd64",
                "Config": {"Labels": {"org.opencontainers.image.revision": SOURCE}}}

    def inspections(self):
        result = {}
        for service, cfg in self.lab["services"].items():
            result[service] = {
                "Id": service + "-synthetic", "Image": self.evidence()["rollback"]["image_id"],
                "Config": {"Env": [k + "=" + str(v) for k, v in cfg["environment"].items()],
                           "Labels": {"com.docker.compose.project": PROJECT, "com.docker.compose.service": service}},
                "HostConfig": {"Memory": 268435456, "NanoCpus": 500000000}, "RestartCount": 0,
                "State": {"Running": True, "Health": {"Status": "healthy"}, "OOMKilled": False, "StartedAt": "2026-10-30T00:00:00Z"},
                "NetworkSettings": {"Networks": {PROJECT + "_default": {}}},
                "Mounts": [{"Type": "volume", "Name": self.lab["volumes"][m["source"]]["name"], "Destination": m["target"], "RW": True} for m in cfg["volumes"]],
            }
        return result

    def test_real_compose_has_only_the_image_build_change(self):
        validate_delta(self.lab, self.prod)
        validate_delta(self.lab, self.overlay)
        self.assertEqual(self.prod, self.overlay)
        self.assertEqual(self.prod["services"]["api"]["image"], IMAGE)

    def test_rejects_environment_mount_network_quota_db_and_build_drift(self):
        mutations = [
            lambda c: c["services"]["api"]["environment"].update(CAMPUSMARKET_DB_HOST="other"),
            lambda c: c["services"]["api"]["volumes"].clear(),
            lambda c: c["networks"]["default"].update(name="other"),
            lambda c: c["services"]["api"]["deploy"]["resources"]["limits"].update(memory="536870912"),
            lambda c: c["services"]["db"].update(image="mysql:latest"),
            lambda c: c["services"]["api"].update(build={"context": "/tmp"}),
            lambda c: c["services"].update(proxy={"image": "nginx"}),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(self.prod)
            mutate(changed)
            with self.subTest(mutation=mutations.index(mutate)), self.assertRaises(Blocked):
                validate_delta(self.lab, changed)

    def test_each_external_gate_is_required_and_does_not_leak_values(self):
        validate_attestations(self.evidence(), PROJECT)
        for gate in GATES:
            data = self.evidence()
            del data["gates"][gate]
            with self.subTest(gate=gate), self.assertRaisesRegex(Blocked, gate):
                validate_attestations(data, PROJECT)

    def test_old_undated_cross_project_or_fake_ci_evidence_is_rejected(self):
        mutations = [
            lambda d: d.update(checked_at=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()),
            lambda d: d.update(checked_at="2026-10-30T00:00:00"),
            lambda d: d.update(project="other"),
            lambda d: d.update(scope="synthetic-ci"),
            lambda d: d["rollback"].update(archive_sha256=""),
        ]
        for mutate in mutations:
            data = self.evidence()
            mutate(data)
            with patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}), self.assertRaises(Blocked):
                validate_attestations(data, PROJECT)

    def test_digest_config_id_and_revision_are_separate_checks(self):
        validate_image(self.image())
        for key, value in (("Id", "sha256:" + "0" * 64), ("RepoDigests", []), ("Architecture", "arm64")):
            image = self.image()
            image[key] = value
            with self.subTest(key=key), self.assertRaises(Blocked):
                validate_image(image)
        image = self.image()
        image["Config"]["Labels"]["org.opencontainers.image.revision"] = "b" * 40
        with self.assertRaises(Blocked):
            validate_image(image)

    def test_actual_mounts_environment_routing_and_health_must_match(self):
        inspections = self.inspections()
        snapshot(self.lab, inspections.__getitem__)
        mutations = [
            lambda d: d["db"]["Mounts"].clear(),
            lambda d: d["api"]["Mounts"][0].update(Name="different_volume"),
            lambda d: d["api"]["Config"].update(Env=[]),
            lambda d: d["api"]["Config"]["Labels"].update({"traefik.http.routers.synthetic.rule": "Host(`synthetic.test`)"}),
            lambda d: d["api"]["State"]["Health"].update(Status="unhealthy"),
            lambda d: d["db"]["HostConfig"].update(Memory=0),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(inspections)
            mutate(changed)
            with self.assertRaises(Blocked) as error:
                snapshot(self.lab, changed.__getitem__)
            self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", str(error.exception))

    def test_plan_is_private_read_only_and_targets_only_api_in_both_directions(self):
        inspections = self.inspections()
        previous = self.evidence()["rollback"]["image_id"]
        rollback = copy.deepcopy(self.prod)
        rollback["services"]["api"]["image"] = previous
        replies = [json.dumps(self.lab), json.dumps(self.prod), json.dumps([self.image()]), json.dumps([{"Id": previous}]), json.dumps(rollback)]
        with tempfile.TemporaryDirectory() as temp, patch("scripts.preparar_despliegue_web.command", side_effect=replies) as execute, patch("scripts.preparar_despliegue_web.inspect_services", return_value=snapshot(self.lab, inspections.__getitem__)):
            out = Path(temp) / "plan"
            plan = prepare(["docker", "compose", "--project-name", PROJECT], self.evidence(), out)
            for key in ("promote", "rollback"):
                self.assertEqual(plan[key][-len(UP_API):], UP_API)
                self.assertNotIn("--build", plan[key])
                self.assertNotIn("--remove-orphans", plan[key])
            for call in execute.call_args_list:
                self.assertNotIn("up", call.args[0])
                self.assertNotIn("exec", call.args[0])
            self.assertEqual(stat.S_IMODE((out / "plan.json").stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o700)
            self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", (out / "plan.json").read_text())
            self.assertEqual(json.loads((out / "rollback.compose.json").read_text()), {"services": {"api": {"image": previous}}})

    def test_verification_refuses_a_db_restart_even_with_same_id(self):
        baseline = snapshot(self.lab, self.inspections().__getitem__)
        current = copy.deepcopy(baseline)
        current["db"]["started_at"] = "changed"
        plan = {"compose_prefix": ["docker", "compose"], "baseline": baseline}
        with patch("scripts.preparar_despliegue_web.command", return_value=json.dumps(self.prod)), patch("scripts.preparar_despliegue_web.inspect_services", return_value=current), self.assertRaisesRegex(Blocked, "MySQL"):
            verify(plan, "promoted")

    def test_command_errors_never_expose_environment_or_stderr(self):
        result = subprocess.CompletedProcess([], 1, stdout="SYNTHETIC_PRIVATE_SENTINEL", stderr="PRIVATE_ERROR")
        with patch("scripts.preparar_despliegue_web.subprocess.run", return_value=result), self.assertRaises(Blocked) as error:
            command(["docker", "inspect", "synthetic"])
        self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", str(error.exception))
        self.assertNotIn("PRIVATE_ERROR", str(error.exception))


if __name__ == "__main__":
    unittest.main()
