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
    config_digest,
    inventory,
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

    def plan(self):
        prefix = ["docker", "compose", "--project-name", PROJECT, "--env-file", "/private/synthetic.env",
                  "-f", str(ROOT / "deploy/compose.lab.yaml"), "-f", str(ROOT / "deploy/compose.web.yaml")]
        baseline = snapshot(self.lab, self.inspections().__getitem__)
        previous = baseline["api"]["image_id"]
        rollback = copy.deepcopy(self.prod)
        rollback["services"]["api"]["image"] = previous
        return {"project": PROJECT, "candidate": IMAGE, "candidate_image_id": IMAGE_ID, "source_sha": SOURCE,
                "compose_prefix": prefix, "promote": prefix + UP_API,
                "rollback": prefix + ["-f", "/private/rollback.compose.json"] + UP_API,
                "rollback_image_id": previous, "baseline": baseline, "external_evidence": self.evidence(),
                "config_digests": {"ready": config_digest(self.lab), "promoted": config_digest(self.prod), "rollback": config_digest(rollback)}}

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

    def test_null_number_and_empty_references_are_not_evidence(self):
        for reference in (None, 123, True, [], {}, " "):
            data = self.evidence()
            data["gates"]["consistent_backup_restored"]["evidence"] = reference
            with self.subTest(reference=reference), self.assertRaises(Blocked):
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
            plan = prepare(self.plan()["compose_prefix"][:-2], self.evidence(), out)
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
        plan = self.plan()
        with patch("scripts.preparar_despliegue_web.command", return_value=json.dumps(self.prod)), patch("scripts.preparar_despliegue_web.inspect_services", return_value=current), self.assertRaisesRegex(Blocked, "MySQL"):
            verify(plan, "promoted")

    def test_consistently_missing_mounts_do_not_pass_as_persistence(self):
        config = copy.deepcopy(self.lab)
        inspections = self.inspections()
        config["services"]["db"]["volumes"] = []
        inspections["db"]["Mounts"] = []
        with self.assertRaisesRegex(Blocked, "volumen persistente"):
            snapshot(config, inspections.__getitem__)

    def test_altered_plan_never_executes_a_command(self):
        mutations = [
            lambda p: p.update(compose_prefix=["sh", "-c", "PRIVATE_SENTINEL"]),
            lambda p: p["compose_prefix"].extend(["run", "api"]),
            lambda p: p["promote"].append("db"),
            lambda p: p["rollback"].append("--build"),
            lambda p: p.update(candidate_image_id="sha256:" + "f" * 64),
        ]
        for mutate in mutations:
            plan = self.plan()
            mutate(plan)
            with patch("scripts.preparar_despliegue_web.command") as execute, self.assertRaises(Blocked):
                verify(plan, "promoted")
            execute.assert_not_called()

    def test_configuration_drift_is_rejected_before_inspecting_containers(self):
        changed = copy.deepcopy(self.prod)
        changed["services"]["api"]["environment"]["CAMPUSMARKET_CORS_ORIGINS"] = "https://synthetic.test"
        with patch("scripts.preparar_despliegue_web.command", return_value=json.dumps(changed)), patch("scripts.preparar_despliegue_web.inspect_services") as inspect, self.assertRaisesRegex(Blocked, "Configuración cambió"):
            verify(self.plan(), "promoted")
        inspect.assert_not_called()

    def test_ready_requires_fresh_evidence_and_unchanged_containers(self):
        plan = self.plan()
        with patch("scripts.preparar_despliegue_web.command", return_value=json.dumps(self.lab)), patch("scripts.preparar_despliegue_web.inspect_services", return_value=plan["baseline"]):
            verify(plan, "ready")
        plan["external_evidence"]["checked_at"] = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        with patch("scripts.preparar_despliegue_web.command") as execute, self.assertRaises(Blocked):
            verify(plan, "ready")
        execute.assert_not_called()

    def test_inventory_queries_only_this_project_and_remains_blocked(self):
        data = self.inspections()
        selected = []
        for service in ("api", "db"):
            raw = data[service]
            selected.append({"project": PROJECT, "service": service, "image_id": raw["Image"],
                             "mounts": [{"type": m["Type"], "name": m["Name"], "target": m["Destination"], "rw": m["RW"]} for m in raw["Mounts"]]})
        replies = ["a" * 64, json.dumps(selected[0]), "b" * 64, json.dumps(selected[1]), json.dumps({"image_id": data["api"]["Image"]}), Blocked("PRIVATE_STDERR")]
        with patch("scripts.preparar_despliegue_web.command", side_effect=replies) as execute:
            report = inventory(PROJECT)
        self.assertTrue(report["mounts_observed"])
        self.assertTrue(report["production_deployment_blocked"])
        self.assertFalse(report["rollback_recovery_verified"])
        self.assertFalse(report["backup_restore_verified"])
        self.assertFalse(report["ghcr_server_pull_verified"])
        self.assertFalse(report["candidate_cache"]["metadata_read"])
        self.assertNotIn("PRIVATE_STDERR", json.dumps(report))
        for call in execute.call_args_list:
            self.assertNotIn(".Env", " ".join(call.args[0]))
            self.assertNotIn(".Source", " ".join(call.args[0]))
            self.assertNotIn("pull", call.args[0])
            self.assertNotIn("exec", call.args[0])
            if call.args[0][1] == "ps":
                self.assertIn("label=com.docker.compose.project=" + PROJECT, call.args[0])

    def test_inventory_rejects_other_projects_before_querying_docker(self):
        with patch("scripts.preparar_despliegue_web.command") as execute, self.assertRaises(Blocked):
            inventory("other-team-project")
        execute.assert_not_called()

    def test_command_errors_never_expose_environment_or_stderr(self):
        result = subprocess.CompletedProcess([], 1, stdout="SYNTHETIC_PRIVATE_SENTINEL", stderr="PRIVATE_ERROR")
        with patch("scripts.preparar_despliegue_web.subprocess.run", return_value=result), self.assertRaises(Blocked) as error:
            command(["docker", "inspect", "synthetic"])
        self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", str(error.exception))
        self.assertNotIn("PRIVATE_ERROR", str(error.exception))


@unittest.skipUnless(os.environ.get("GITHUB_ACTIONS") == "true", "Solo daemon efímero del runner: no usar Docker local/productivo")
class DockerInventoryTests(unittest.TestCase):
    def test_real_selectors_exclude_environment_and_volume_contents(self):
        from scripts.ensayar_imagen_ghcr import project_from_environment

        project = project_from_environment(os.environ)
        endpoint = command(["docker", "context", "inspect", "default", "--format", "{{.Endpoints.docker.Host}}"])
        self.assertEqual(endpoint.strip(), "unix:///var/run/docker.sock")
        created = {"containers": [], "volumes": []}
        image_id = None
        try:
            # TAR vacío importado: no build, pull ni contenedor en ejecución.
            imported = subprocess.run(["docker", "import", "--change", "ENV SYNTHETIC_SECRET=PRIVATE_SENTINEL", "-"], input=b"\0" * 10240, capture_output=True, check=False)
            self.assertEqual(imported.returncode, 0, "No se pudo crear la imagen vacía de prueba; salida privada omitida")
            image_id = imported.stdout.decode().strip()
            for service, destination in (("api", "/app/backend/uploads"), ("db", "/var/lib/mysql")):
                name = project + "-inventory-" + service
                self.assertEqual(command(["docker", "volume", "ls", "-q", "--filter", "name=^" + name + "$"]).strip(), "")
                command(["docker", "volume", "create", "--label", "com.docker.compose.project=" + project, name])
                created["volumes"].append(name)
                cid = command(["docker", "create", "--label", "com.docker.compose.project=" + project,
                               "--label", "com.docker.compose.service=" + service, "--memory", "256m", "--cpus", "0.5",
                               "--mount", "type=volume,source=" + name + ",target=" + destination, image_id, "/bin/true"]).strip()
                created["containers"].append(cid)
            report = inventory(project)
            self.assertTrue(report["mounts_observed"])
            self.assertEqual(report["active_api_image"]["image_id"], image_id)
            self.assertEqual({item["state"] for item in report["containers"].values()}, {"created"})
            self.assertNotIn("PRIVATE_SENTINEL", json.dumps(report))
            self.assertNotIn("SYNTHETIC_SECRET", json.dumps(report))
            self.assertTrue(report["production_deployment_blocked"])
        finally:
            for cid in created["containers"]:
                command(["docker", "rm", cid])
            for name in created["volumes"]:
                command(["docker", "volume", "rm", name])
            if image_id:
                command(["docker", "image", "rm", image_id])


if __name__ == "__main__":
    unittest.main()
