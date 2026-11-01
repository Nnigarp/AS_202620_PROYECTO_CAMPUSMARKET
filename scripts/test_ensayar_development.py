"""Rechazos relevantes de Compose y del acceso a un daemon ajeno; sin Docker Engine."""

import copy
import json
import os
import re
import secrets
import subprocess
import unittest

from scripts.ensayar_development import (
    COMPOSE,
    FORK,
    TrialError,
    project_name,
    validate_config,
)

PROJECT = "campusmarket-development-123-1"


class DevelopmentConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        binary = os.environ.get("CM_COMPOSE_BINARY")
        cls.compose = [binary] if binary else ["docker", "compose"]
        cls.env = {**os.environ, "DEV_MYSQL_PASSWORD": secrets.token_hex(24), "DEV_MYSQL_ROOT_PASSWORD": secrets.token_hex(24),
                   "MYSQL_DATABASE": "must_not_be_used", "MYSQL_USER": "must_not_be_used", "MYSQL_PASSWORD": "must_not_be_used"}
        result = subprocess.run(cls.compose + ["--project-name", PROJECT, "-f", str(COMPOSE), "config", "--format", "json"],
                                env=cls.env, text=True, capture_output=True, check=True)
        cls.config = json.loads(result.stdout)

    def rejected(self, change):
        cfg = copy.deepcopy(self.config)
        change(cfg)
        with self.assertRaises(TrialError):
            validate_config(cfg, PROJECT)

    def test_real_compose_uses_new_credentials_and_fixed_synthetic_database(self):
        validate_config(self.config, PROJECT)
        keys = set(re.findall(r"(?<!\$)\$\{([A-Z_]+)", COMPOSE.read_text()))
        self.assertEqual(keys, {"DEV_MYSQL_PASSWORD", "DEV_MYSQL_ROOT_PASSWORD"})
        self.assertNotIn("must_not_be_used", json.dumps(self.config))

    def test_missing_development_credentials_fails_even_with_generic_mysql_credentials(self):
        env = {k: v for k, v in self.env.items() if not k.startswith("DEV_MYSQL_")}
        r = subprocess.run(self.compose + ["--project-name", PROJECT, "-f", str(COMPOSE), "config", "--quiet"],
                           env=env, text=True, capture_output=True, check=False)
        self.assertNotEqual(r.returncode, 0)

    def test_rejects_other_project(self):
        with self.assertRaises(TrialError):
            validate_config(self.config, "campusmarket-sistema-2zvsxj")

    def test_rejects_production_database_or_user_or_origin(self):
        for field in ("CAMPUSMARKET_DB_HOST", "CAMPUSMARKET_DB_NAME", "CAMPUSMARKET_DB_USER", "CAMPUSMARKET_CORS_ORIGINS"):
            with self.subTest(field=field):
                self.rejected(lambda c, field=field: c["services"]["api"]["environment"].update({field: "production"}))

    def test_rejects_external_or_global_volumes(self):
        for value in ({"external": True}, {"name": "campusmarket-sistema-2zvsxj_mysql_data"}, {"driver_opts": {"device": "/data"}}):
            with self.subTest(value=value):
                self.rejected(lambda c, value=value: c["volumes"]["dev_mysql_data"].update(value))

    def test_rejects_bind_mount_or_shared_network(self):
        self.rejected(lambda c: c["services"]["api"]["volumes"][0].update(type="bind", source="/data"))
        self.rejected(lambda c: c["networks"]["default"].update(name="production_default"))
        self.rejected(lambda c: c["networks"]["dev_data"].update(internal=False))
        self.rejected(lambda c: c["services"]["db"]["networks"].update(default=None))

    def test_rejects_build_mutable_api_or_published_ports(self):
        for field, value in (("build", {"context": "."}), ("image", "ghcr.io/nnigarp/campusmarket-web-candidate:latest"),
                             ("ports", [{"target": 8000, "published": "8000"}]), ("privileged", True)):
            with self.subTest(field=field):
                self.rejected(lambda c, field=field, value=value: c["services"]["api"].update({field: value}))

    def test_rejects_mutable_mysql_reference_for_panel_rollback(self):
        self.rejected(lambda c: c["services"]["db"].update(image="mysql:8.4"))

    def test_rejects_changed_limits_or_missing_healthcheck(self):
        self.rejected(lambda c: c["services"]["api"]["deploy"]["resources"]["limits"].update(memory="0"))
        self.rejected(lambda c: c["services"]["db"].pop("healthcheck"))

    def test_runner_guard_accepts_only_ephemeral_fork_run(self):
        env = {"GITHUB_REPOSITORY": FORK, "GITHUB_ACTIONS": "true", "RUNNER_ENVIRONMENT": "github-hosted",
               "GITHUB_SERVER_URL": "https://github.com", "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1", "GITHUB_SHA": "a" * 40}
        self.assertEqual(project_name(env), PROJECT)
        self.assertEqual(project_name(env, control=True), PROJECT + "-control")
        for key, value in (("GITHUB_REPOSITORY", "ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET"), ("DOCKER_HOST", "ssh://server"),
                           ("DOCKER_CONTEXT", "production"), ("RUNNER_ENVIRONMENT", "self-hosted"), ("GITHUB_RUN_ID", "../production")):
            with self.subTest(key=key), self.assertRaises(TrialError):
                project_name({**env, key: value})


if __name__ == "__main__":
    unittest.main()
