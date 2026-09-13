"""TODO23 Phase 4 — deployment surface: substrate compilation, export,
quantization, energy estimation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import torch
from computronium_lab import Lab
from computronium_lab.deployment import (
    compile_substrate,
    estimate_energy,
    export_system,
    substrate_report,
)
from computronium_lab.presets import build_system_preset
from computronium_lab.synthesis.spec import Constraints


@pytest.fixture(scope="module")
def system():
    return build_system_preset("backprop_mlp", input_dim=32, output_dim=4)


def test_compile_substrate_defaults():
    spec = compile_substrate(Constraints(substrate="memristive"))
    assert spec.device_model.value == "memristive"
    assert spec.structural_constraints.weight_bounds == (0.0, 1.0)
    assert spec.noise_model.level > 0
    digital = compile_substrate(Constraints(substrate="digital"))
    assert digital.device_model.value == "digital"
    assert digital.cost_model.joules_per_mac > 0


def test_apply_substrate_constraints_bounded(system):
    from computronium_lab.deployment import apply_substrate_constraints

    from computronium.ontology.substrate.spec import make_substrate

    spec = compile_substrate(Constraints(substrate="memristive"))
    apply_substrate_constraints(system.geometry, make_substrate(spec))  # type: ignore[arg-type]
    weights = [
        p
        for name, p in system.geometry.named_parameters()  # type: ignore[attr-defined]
        if "weight" in name
    ]
    assert weights and all(w.min() >= 0.0 for w in weights)


def test_substrate_report_fidelity(system):
    spec = compile_substrate(Constraints(substrate="memristive"))
    x = torch.randn(4, 32)
    report = substrate_report(system.geometry, spec, x)  # type: ignore[arg-type]
    assert report.constraints_preserved
    assert report.fidelity_max_abs_diff >= 0.0


def test_energy_estimate_tiers(system):
    spec = compile_substrate(Constraints(substrate="digital"))
    sim = estimate_energy(system.geometry, spec, tier="simulated")  # type: ignore[arg-type]
    est = estimate_energy(system.geometry, spec, tier="estimated")  # type: ignore[arg-type]
    assert sim.macs > 0
    assert sim.joules < est.joules  # simulated tier uses the cheaper device coeff
    assert sim.tier == "simulated" and est.tier == "estimated"


@pytest.mark.parametrize("quantization", [None, "int8", "ternary"])
def test_export_system_manifest(tmp_path: Path, system, quantization):
    result = export_system(
        system,
        str(tmp_path),
        constraints=Constraints(substrate="memristive"),
        target="onnx",
        quantization=quantization,
        input_shape=(1, 32),
    )
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["target"] == "onnx"
    assert manifest["substrate"]["device"] == "memristive"
    assert "energy" in manifest and manifest["energy"]["macs"] > 0
    assert Path(result.state_dict_path).exists()
    if quantization is not None:
        assert result.quantization is not None


def test_export_unknown_target_rejected(tmp_path: Path, system):
    with pytest.raises(ValueError, match="unknown target"):
        export_system(system, str(tmp_path), target="scsi")


def test_lab_export_entrypoint(tmp_path: Path):
    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")
    spec = lab.specify(
        "classification",
        "synthetic",
        constraints=Constraints(substrate="digital", precision="float32"),
    )
    result = lab.export(
        system, str(tmp_path), spec=spec, target="onnx", input_shape=(1, 32)
    )
    assert Path(result.manifest_path).exists()


def test_lab_serve_builds_server_only_stub():
    # serve_system is the blocking FastAPI runner; verify the wrapped module
    # contract it relies on instead of opening a socket.
    from computronium_lab.deployment import _GeometryModule

    system = build_system_preset("backprop_mlp", input_dim=32, output_dim=4)
    model = _GeometryModule(system.geometry, None)  # type: ignore[attr-defined]
    model.eval()
    with torch.no_grad():
        y = model(torch.randn(2, 32))
    assert y.shape == (2, 4)
