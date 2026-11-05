"""Controles que impiden usar el ensayo S14 contra recursos productivos."""
import os
import subprocess
import unittest
from unittest.mock import patch

from scripts import medir_ec01_s14 as experiment


class SafetyAndCriterionTests(unittest.TestCase):
    def environment(self, **changes):
        return {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": "Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET",
                "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1", **changes}

    def test_outside_ci_never_calls_docker(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(experiment, "command") as command:
            with self.assertRaises(RuntimeError):
                experiment.prepare()
            command.assert_not_called()

    def test_remote_daemon_rejected(self):
        with patch.dict(os.environ, self.environment(DOCKER_HOST="ssh://production"), clear=True), self.assertRaises(RuntimeError):
            experiment.guard()

    def test_other_repository_rejected(self):
        with patch.dict(os.environ, self.environment(GITHUB_REPOSITORY="other/project"), clear=True), self.assertRaises(RuntimeError):
            experiment.guard()

    def test_arbitrary_project_in_run_id_rejected(self):
        with patch.dict(os.environ, self.environment(GITHUB_RUN_ID="campusmarket-sistema"), clear=True), self.assertRaises(RuntimeError):
            experiment.guard()

    def test_public_or_authority_urls_never_sent(self):
        with patch.object(experiment.urllib.request, "urlopen") as open_url:
            for path in ["https://campusmarket.iscoutb.dev/catalogo", "//campusmarket.iscoutb.dev/catalogo"]:
                with self.assertRaises(RuntimeError):
                    experiment.request(path)
            open_url.assert_not_called()

    def test_nine_of_ten_can_pass_with_p95_above_budget(self):
        samples = [{"ms": 100, "valid": True} for _ in range(9)] + [{"ms": 5000, "valid": True}]
        result = experiment.summarize(samples)
        self.assertEqual(result["within_2000ms"], 9)
        self.assertEqual(result["p95_ms"], 5000)
        self.assertTrue(result["outcome"].startswith("CUMPLE"))

    def test_incomplete_response_not_counted_as_fast_success(self):
        samples = [{"ms": 100, "valid": True} for _ in range(8)] + [{"ms": 10, "valid": False} for _ in range(2)]
        result = experiment.summarize(samples)
        self.assertEqual(result["within_2000ms"], 8)
        self.assertEqual(result["outcome"], "NO CUMPLE")

    def test_no_sample_silently_removed(self):
        with self.assertRaises(RuntimeError):
            experiment.summarize([{"ms": 100, "valid": True}] * 9)

    def test_private_process_output_not_exposed(self):
        completed = subprocess.CompletedProcess(["docker"], 1, stdout="private-environment", stderr="private-password")
        with patch.object(experiment.subprocess, "run", return_value=completed):
            with self.assertRaises(RuntimeError) as error:
                experiment.command(["docker"])
            self.assertNotIn("private", str(error.exception))


if __name__ == "__main__":
    unittest.main()
