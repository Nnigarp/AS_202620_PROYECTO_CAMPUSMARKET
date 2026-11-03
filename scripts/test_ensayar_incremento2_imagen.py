"""Verificar que errores de contexto no ejecutan Docker ni divulgan Environment."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import ensayar_incremento2_imagen as subject


class GuardTests(unittest.TestCase):
    def test_fuera_de_ci_no_se_limpia_nada(self):
        with patch.dict("os.environ", {}, clear=True), patch.object(subject, "command") as docker:
            with self.assertRaises(AssertionError):
                subject.cleanup()
            docker.assert_not_called()

    def test_identificador_no_numerico_no_ejecuta_docker(self):
        with patch.dict("os.environ", {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "production", "GITHUB_RUN_ATTEMPT": "1"}, clear=True):
            with patch.object(subject, "command") as docker, self.assertRaises(AssertionError):
                subject.cleanup()
            docker.assert_not_called()

    def test_estado_de_produccion_no_se_puede_limpiar(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps({"project": "campusmarket-sistema-2zvsxj"}))
            with (
                patch.dict("os.environ", {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1"}, clear=True),
                patch.object(subject, "STATE", path), patch.object(subject, "command") as docker,
            ):
                with self.assertRaises(AssertionError):
                    subject.cleanup()
                docker.assert_not_called()

    def test_estado_de_otro_run_no_se_limpia(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps({"project": "cm-i2-999-1"}))
            with (
                patch.dict("os.environ", {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1"}, clear=True),
                patch.object(subject, "STATE", path), patch.object(subject, "command") as docker,
            ):
                with self.assertRaises(AssertionError):
                    subject.cleanup()
                docker.assert_not_called()

    def test_error_no_refleja_credenciales_de_infraestructura(self):
        failed = SimpleNamespace(returncode=1, stdout="clave-sintetica", stderr="Environment privado")
        with patch.object(subject.subprocess, "run", return_value=failed):
            with self.assertRaises(RuntimeError) as error:
                subject.command(["docker", "-e", "PASSWORD=clave-sintetica"])
            self.assertNotIn("clave-sintetica", str(error.exception))
            self.assertNotIn("Environment", str(error.exception))


if __name__ == "__main__":
    unittest.main()
