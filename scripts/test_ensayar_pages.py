"""Controles de destino y artefactos; sin acceso a la API real."""

import tempfile
import unittest
from pathlib import Path

from scripts.ensayar_pages import (
    API,
    BASE_HREF,
    Rejected,
    api_path,
    file_manifest,
    validate_bundle,
)


class PagesChecks(unittest.TestCase):
    def test_http_write_and_private_or_external_paths_are_rejected(self):
        for method, path in (("POST", "/publicaciones"), ("DELETE", "/catalogo/1"), ("GET", "/usuarios/me"),
                             ("GET", "https://other.invalid/health"), ("GET", "/catalogo/1?token=private"), ("GET", "/uploads/../.env")):
            with self.subTest(method=method, path=path), self.assertRaises(Rejected):
                api_path(method, path)
        api_path("GET", "/catalogo/1")
        api_path("OPTIONS", "/usuarios/login")

    def test_bundle_requires_pages_base_api_and_no_private_files(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "main.dart.js").write_text(API)
            (site / "index.html").write_text('<base href="/app/">')
            with self.assertRaises(Rejected):
                validate_bundle(site)
            (site / "index.html").write_text('<base href="' + BASE_HREF + '">')
            validate_bundle(site)
            (site / ".env").write_text("synthetic")
            with self.assertRaises(Rejected):
                validate_bundle(site)

    def test_manifest_detects_changed_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "index.html").write_text("first")
            before = file_manifest(site)
            (site / "index.html").write_text("second")
            self.assertNotEqual(before, file_manifest(site))


if __name__ == "__main__":
    unittest.main()
