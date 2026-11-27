"""Prueba el código de salida del mismo comando que ejecuta CI."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class DocumentacionTest(unittest.TestCase):
    def setUp(self):
        directorio = tempfile.TemporaryDirectory()
        self.addCleanup(directorio.cleanup)
        self.root = Path(directorio.name)
        (self.root / "docs").mkdir()
        self.aspectos = self.root / "docs/aspectos.md"
        self.aspectos.write_text(
            "| ID | Aspecto | Requisito | C4 | ADR | Código | Pruebas | Evidencia |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| A | B | C | D | E | F | G | H |\n", encoding="utf-8"
        )

    def verificar(self, esperado):
        script = Path(__file__).with_name("verificar_documentacion.py")
        proceso = subprocess.run([sys.executable, script, self.root], capture_output=True, check=False)
        self.assertEqual(proceso.returncode, esperado, proceso.stdout + proceso.stderr)
        return proceso.stdout

    def test_valido(self):
        self.verificar(0)

    def test_enlace_roto(self):
        (self.root / "README.md").write_text("[guía](ausente.md)", encoding="utf-8")
        self.assertIn(b"MISSING_PATH", self.verificar(1))

    def test_fila_incompleta(self):
        texto = self.aspectos.read_text(encoding="utf-8").replace("| G | H |", "| G |")
        self.aspectos.write_text(texto, encoding="utf-8")
        self.assertIn(b"columnas escritas", self.verificar(1))
