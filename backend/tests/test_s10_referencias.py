"""Git local sintético: sin producción, credenciales ni dependencia de HEAD^1."""

import json
import subprocess
from pathlib import Path

import pytest

from scripts.preparar_s10_referencias import CONTRACT, git, prepare


def command(root: Path, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def commit(root: Path, message: str) -> str:
    command(root, "add", ".")
    command(root, "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def repository(path: Path) -> Path:
    path.mkdir()
    command(path, "init", "-b", "master")
    command(path, "config", "user.name", "S10 Synthetic")
    command(path, "config", "user.email", "s10@campus.test")
    return path


@pytest.fixture
def histories(tmp_path):
    official = repository(tmp_path / "official")
    (official / "README.md").write_text("Revisión runtime sin contrato versionado\n")
    runtime = commit(official, "runtime marker")
    baseline = {"openapi": "3.1.0", "paths": {"/health": {"get": {"operationId": "salud"}}}}
    contract_file = official / CONTRACT
    contract_file.parent.mkdir()
    contract_file.write_text(json.dumps(baseline))
    deployed_contract = commit(official, "contrato de interfaz desplegada")
    candidate = repository(tmp_path / "candidate")
    (candidate / "contracts").mkdir()
    proposed = {**baseline, "paths": {**baseline["paths"], "/favoritos": {"get": {"operationId": "favoritos"}}}}
    (candidate / CONTRACT).write_text(json.dumps(proposed))
    (candidate / ".github").mkdir()
    (candidate / ".github/s10-produccion.json").write_text(json.dumps({
        "contract_commit": deployed_contract, "runtime_revision": runtime,
        "image": "ghcr.io/synthetic/app@sha256:" + "a" * 64,
    }))
    source = commit(candidate, "candidato sin HEAD padre")
    return official, candidate, runtime, deployed_contract, source, baseline, proposed


def test_master_real_revision_y_candidato_son_referencias_independientes(histories, tmp_path):
    official, candidate, runtime, baseline_sha, source, baseline, proposed = histories
    # La revisión reportada no tiene el fichero, exactamente el defecto del PR.
    with pytest.raises(subprocess.CalledProcessError):
        git(official, "show", f"{runtime}:{CONTRACT}")
    # El candidato no tiene HEAD^1: tampoco se puede usar como sustituto de base.
    with pytest.raises(subprocess.CalledProcessError):
        git(candidate, "rev-parse", "HEAD^1")
    output = tmp_path / "references"
    result = prepare(candidate, output, upstream=str(official))
    assert result["official_master_sha"] == baseline_sha
    assert result["candidate_sha"] == source
    assert result["expected_runtime_revision"] == runtime
    assert result["reference_contract_sha"] == baseline_sha != runtime
    assert json.loads((output / "reference-contract.json").read_text()) == baseline
    assert json.loads((output / "candidate-contract.json").read_text()) == proposed
    assert result["contract_sha256"]["candidate"] != result["contract_sha256"]["reference"]


def test_merge_futuro_no_exige_contrato_nuevo_a_produccion(histories, tmp_path):
    official, candidate, runtime, baseline_sha, _, baseline, proposed = histories
    (official / CONTRACT).write_text(json.dumps(proposed))
    current_master = commit(official, "merge del incremento sin desplegar")
    result = prepare(candidate, tmp_path / "references", upstream=str(official))
    assert result["official_master_sha"] == current_master != baseline_sha
    assert result["production_contract_sha"] == baseline_sha
    assert result["expected_runtime_revision"] == runtime
    assert json.loads((tmp_path / "references/reference-contract.json").read_text()) == baseline


def test_posdespliegue_usa_contrato_y_revision_de_imagen_exacta(histories, tmp_path):
    official, candidate, _, _, orchestrator, _, proposed = histories
    (official / CONTRACT).write_text(json.dumps(proposed))
    source = commit(official, "imagen instalada anterior a la corrección de workflow")
    result = prepare(candidate, tmp_path / "references", upstream=str(official),
                     mode="instalado", expected_revision=source)
    assert result["expected_runtime_revision"] == result["reference_contract_sha"] == source
    assert result["orchestration_sha"] == orchestrator != source
    assert json.loads((tmp_path / "references/reference-contract.json").read_text()) == proposed


@pytest.mark.parametrize("revision", ["", "HEAD", "a" * 40])
def test_posdespliegue_rechaza_revision_invalida_o_inexistente(histories, tmp_path, revision):
    official, candidate, *_ = histories
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        prepare(candidate, tmp_path / "references", upstream=str(official),
                mode="instalado", expected_revision=revision)


def test_no_sustituye_referencia_inexistente_por_respuesta_http(histories, tmp_path):
    official, candidate, runtime, *_ = histories
    config = candidate / ".github/s10-produccion.json"
    values = json.loads(config.read_text())
    values["contract_commit"] = runtime
    config.write_text(json.dumps(values))
    commit(candidate, "referencia incorrecta")
    with pytest.raises(subprocess.CalledProcessError):
        prepare(candidate, tmp_path / "references", upstream=str(official))


def test_no_sobrescribe_evidencia_previa(histories, tmp_path):
    official, candidate, *_ = histories
    output = tmp_path / "references"
    prepare(candidate, output, upstream=str(official))
    original = (output / "references.json").read_bytes()
    with pytest.raises(FileExistsError):
        prepare(candidate, output, upstream=str(official))
    assert (output / "references.json").read_bytes() == original
