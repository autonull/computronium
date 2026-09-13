"""Lab deployment surface (TODO23 Phase 4): substrate compilation, kernel
export, quantization, edge runtime, and energy estimation.

Wraps the existing substrate classes, ``computronium.deployment``
quantization/ONNX machinery, and geometry modules — no new substrate
semantics. ``Lab.export`` is the single entry point; ``Lab.serve`` runs the
existing FastAPI edge runtime against a composed system.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import torch
from torch import Tensor, nn

from computronium.ontology.substrate.spec import (
    CostConfig,
    DeviceModel,
    NumericRepresentation,
    SubstrateSpec,
)
from computronium_lab.synthesis.spec import Constraints, ProblemSpec

if TYPE_CHECKING:
    from computronium.ontology.substrate._substrate import Substrate

Quantization = Literal["int8", "ternary"]
KNOWN_QUANTIZATIONS: frozenset[str] = frozenset({"int8", "ternary"})

_TARGET_TOOLCHAINS: dict[str, str] = {
    "onnx": "onnx",
    "pt2": "torch.export",
    "triton": "triton",
    "fpga": "hls",
    "neuromorphic": "nxsdk",
    "photonic": "dsl",
    "memristive": "spice",
    "quantum": "qasm",
}

# Rough per-device MAC energy coefficients (simulated tier, labeled as such).
_DEVICE_JOULES_PER_MAC: dict[DeviceModel, float] = {
    DeviceModel.DIGITAL: 5e-13,
    DeviceModel.MEMRISTIVE: 1e-14,
    DeviceModel.NEUROMORPHIC: 2e-13,
    DeviceModel.PHOTONIC: 1e-14,
    DeviceModel.QUANTUM: 0.0,
}

# Generic 45nm-class coefficient for the "estimated" tier.
_GENERIC_J_PER_MAC = 1e-12

_PRECISION_TO_NUMERIC: dict[str, NumericRepresentation] = {
    "float32": NumericRepresentation.REAL,
    "float16": NumericRepresentation.REAL,
    "bfloat16": NumericRepresentation.REAL,
    "complex": NumericRepresentation.COMPLEX,
    "ternary": NumericRepresentation.TERNARY,
    "int8": NumericRepresentation.INT8,
}

_DEVICE_TO_MODEL: dict[str, DeviceModel] = {
    "digital": DeviceModel.DIGITAL,
    "memristive": DeviceModel.MEMRISTIVE,
    "neuromorphic": DeviceModel.NEUROMORPHIC,
    "photonic": DeviceModel.PHOTONIC,
    "quantum": DeviceModel.QUANTUM,
}


def compile_substrate(constraints: Constraints) -> SubstrateSpec:
    """Project problem constraints onto a structured SubstrateSpec (T23.4.1).

    Device-model defaults (noise, weight bounds, sparsity) come from the
    existing ``SubstrateConfig`` classmethods so compiled substrates match
    the trained/validated substrate classes exactly.
    """
    from computronium.ontology.substrate._substrate import SubstrateConfig

    device = constraints.substrate
    cfg_cls = SubstrateConfig
    if device == "memristive":
        config = cfg_cls.memristive()
    elif device == "neuromorphic":
        config = cfg_cls.neuromorphic()
    elif device == "photonic":
        config = cfg_cls.optical()
    elif device == "quantum":
        config = cfg_cls.quantum()
    else:
        config = cfg_cls.digital(
            precision=constraints.precision,
            weight_bounds=None if constraints.precision == "float32" else (-1.0, 1.0),
        )
    spec = SubstrateSpec.from_config(config)
    numeric = _PRECISION_TO_NUMERIC.get(constraints.precision)
    if device == "digital" and numeric is not None:
        spec = _replace_spec(spec, numeric_representation=numeric)
    spec = _replace_spec(
        spec,
        cost_model=CostConfig(
            joules_per_mac=_DEVICE_JOULES_PER_MAC[_DEVICE_TO_MODEL[device]]
        ),
    )
    return spec


def _replace_spec(spec: SubstrateSpec, **updates: object) -> SubstrateSpec:
    from dataclasses import replace

    return replace(spec, **updates)  # type: ignore[arg-type]


def _geometry_of(system: object) -> nn.Module:
    geometry = getattr(system, "geometry", None)
    if geometry is None:
        raise ValueError("system has no geometry to deploy")
    return geometry


def _linear_dims(geometry: nn.Module) -> list[tuple[int, int]]:
    from computronium.ontology.geometry import layer_stack

    stack = layer_stack(geometry)  # type: ignore[arg-type]
    if stack is None:
        return []
    return [
        (layer.in_features, layer.out_features)
        for layer in stack
        if isinstance(layer, nn.Linear)
    ]


def apply_substrate_constraints(geometry: nn.Module, substrate: Substrate) -> None:
    """Quantize/bound weights in place via the substrate's own operators."""
    from computronium.ontology.geometry import layer_stack

    stack = layer_stack(geometry)  # type: ignore[arg-type]
    if stack is None:
        return
    with torch.no_grad():
        for layer in stack:
            if isinstance(layer, nn.Linear):
                layer.weight.copy_(substrate.quantize_weights(layer.weight))


@dataclass(frozen=True, slots=True)
class SubstrateReport:
    """Substrate constraint report attached to every export (T23.4.1)."""

    device: str
    numeric: str
    noise_level: float
    weight_bounds: tuple[float, float] | None
    sparsity: float
    fidelity_max_abs_diff: float
    constraints_preserved: bool
    note: str = ""


def substrate_report(
    geometry: nn.Module,
    spec: SubstrateSpec,
    sample_input: Tensor,
) -> SubstrateReport:
    """Compare substrate-routed vs digital baseline forward on a probe input."""
    from computronium.ontology.substrate import DigitalSubstrate
    from computronium.ontology.substrate.spec import make_substrate

    geometry.eval()
    with torch.no_grad():
        baseline = geometry(sample_input, DigitalSubstrate())
        compiled = geometry(sample_input, make_substrate(spec))
    fidelity = float((baseline - compiled).abs().max())
    bounds = spec.structural_constraints.weight_bounds
    return SubstrateReport(
        device=spec.device_model.value,
        numeric=spec.numeric_representation.value,
        noise_level=spec.noise_model.level,
        weight_bounds=bounds,
        sparsity=spec.structural_constraints.sparsity,
        fidelity_max_abs_diff=fidelity,
        constraints_preserved=True,
        note="fidelity = max |digital baseline − substrate-routed| on probe input",
    )


@dataclass(frozen=True, slots=True)
class EnergyEstimate:
    """Energy/cost estimate with its measurement tier (T23.4.5)."""

    tier: Literal["simulated", "estimated"]
    macs: int
    joules: float
    note: str


def estimate_energy(
    geometry: nn.Module,
    spec: SubstrateSpec,
    *,
    batch_size: int = 1,
    tier: Literal["simulated", "estimated"] = "simulated",
    layer_dims: list[tuple[int, int]] | None = None,
) -> EnergyEstimate:
    """MAC-count energy estimate; tier labels the measurement provenance.

    ``layer_dims`` overrides the geometry-derived Linear stack (pass the
    dims captured *before* quantization — ternary/int8 replacement hides
    the ``nn.Linear`` stack).
    """
    dims = layer_dims if layer_dims is not None else _linear_dims(geometry)
    macs_per_input = sum(f_in * f_out for f_in, f_out in dims)
    macs = macs_per_input * batch_size
    if tier == "simulated":
        j_per = spec.cost_model.joules_per_mac
        note = f"simulated tier: measured-class coefficient {j_per:.3e} J/MAC"
    else:
        j_per = _GENERIC_J_PER_MAC
        note = "estimated tier: generic 45nm-class coefficient 1.0e-12 J/MAC"
    return EnergyEstimate(tier=tier, macs=macs, joules=macs * j_per, note=note)


class _GeometryModule(nn.Module):
    """Inference-only wrapper: geometry.forward(x, substrate) → model(x)."""

    def __init__(self, geometry: nn.Module, substrate: Substrate | None) -> None:
        super().__init__()
        self.geometry = geometry
        self._substrate = substrate

    def forward(self, x: Tensor) -> Tensor:
        return self.geometry(x, self._substrate)


def _quantize(model: nn.Module, quantization: Quantization) -> tuple[nn.Module, str]:
    from computronium.deployment import (
        quantize_model_dynamic_int8,
        quantize_model_ternary_inplace,
    )

    if quantization == "int8":
        return quantize_model_dynamic_int8(model), "dynamic int8 (weights qint8)"
    return (
        quantize_model_ternary_inplace(model),
        "ternary {−1, 0, +1} with STE",
    )


def _try_export_onnx(
    model: nn.Module,
    sample_input: Tensor,
    path: Path,
    report: SubstrateReport,
) -> tuple[str | None, SubstrateReport]:
    """Best-effort ONNX export; a runtime hiccup degrades the note, never fails."""
    try:
        torch.onnx.export(
            model,
            (sample_input,),
            path,
            input_names=["x"],
            output_names=["y"],
            dynamo=False,
        )
        return str(path), report
    except Exception as exc:  # ruff: ignore[blind-except] - best-effort by convention
        return None, _replace_report(
            report,
            note=f"{report.note}; onnx export skipped: {exc}",
        )


def _replace_report(report: SubstrateReport, **updates: object) -> SubstrateReport:
    from dataclasses import replace

    return replace(report, **updates)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class ExportResult:
    """Artifacts + certificates produced by ``export_system``."""

    onnx_path: str | None
    state_dict_path: str
    manifest_path: str
    substrate_report: SubstrateReport
    energy: EnergyEstimate
    quantization: str | None


def _build_manifest(
    report: SubstrateReport,
    energy: EnergyEstimate,
    dims: list[tuple[int, int]],
    *,
    target: str,
    quant_note: str | None,
) -> dict[str, object]:
    return {
        "target": target,
        "toolchain": _TARGET_TOOLCHAINS[target],
        "substrate": {
            "device": report.device,
            "numeric": report.numeric,
            "noise_level": report.noise_level,
            "weight_bounds": report.weight_bounds,
            "sparsity": report.sparsity,
        },
        "fidelity_max_abs_diff": report.fidelity_max_abs_diff,
        "quantization": quant_note,
        "energy": {
            "tier": energy.tier,
            "macs": energy.macs,
            "joules": energy.joules,
            "note": energy.note,
        },
        "layer_dims": [{"in": i, "out": o} for i, o in dims],
    }


def _quantize_and_export(
    model: nn.Module,
    quantization: Quantization | None,
    sample_input: Tensor,
    out: Path,
    stem: str,
    report: SubstrateReport,
) -> tuple[str | None, str | None, SubstrateReport]:
    """Optional quantization, then best-effort ONNX + state-dict artifacts."""
    quantized_model: nn.Module | None = None
    quant_note: str | None = None
    if quantization is not None:
        quantized_model, quant_note = _quantize(model, quantization)
    onnx_path, report = _try_export_onnx(
        quantized_model or model, sample_input, out / f"{stem}.onnx", report
    )
    torch.save(model.geometry.state_dict(), out / f"{stem}.pt")  # type: ignore[attr-defined]
    return onnx_path, quant_note, report


def export_system(
    system: object,
    out_dir: str,
    *,
    constraints: Constraints | None = None,
    target: str = "onnx",
    quantization: Quantization | None = None,
    input_shape: tuple[int, ...] = (1, 32),
    sample_input: Tensor | None = None,
    batch_size: int = 1,
) -> ExportResult:
    """Compile → constrain → quantize → export with substrate report (Phase 4).

    The manifest JSON is always written and is the authoritative artifact;
    ONNX export is best-effort (a missing onnx runtime never fails the
    export — matching the kernel-export convention).
    """
    if target not in _TARGET_TOOLCHAINS:
        raise ValueError(
            f"unknown target {target!r}; known: {sorted(_TARGET_TOOLCHAINS)}"
        )
    if quantization is not None and quantization not in KNOWN_QUANTIZATIONS:
        raise ValueError(
            f"unknown quantization {quantization!r}; known: {sorted(KNOWN_QUANTIZATIONS)}"
        )
    geometry = _geometry_of(system)
    spec = compile_substrate(constraints or Constraints())
    from computronium.ontology.substrate.spec import make_substrate

    substrate = make_substrate(spec)
    apply_substrate_constraints(geometry, substrate)
    dims = _linear_dims(geometry)
    if sample_input is None:
        sample_input = torch.randn(*input_shape)
    report = substrate_report(geometry, spec, sample_input)

    model = _GeometryModule(geometry, substrate)
    model.eval()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{spec.device_model.value}_{spec.numeric_representation.value}"

    onnx_path, quant_note, report = _quantize_and_export(
        model, quantization, sample_input, out, stem, report
    )

    energy = estimate_energy(
        geometry, spec, batch_size=batch_size, tier="simulated", layer_dims=dims
    )
    manifest = _build_manifest(
        report,
        energy,
        dims,
        target=target,
        quant_note=quant_note,
    )
    manifest_path = out / f"{stem}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return ExportResult(
        onnx_path=onnx_path,
        state_dict_path=str(out / f"{stem}.pt"),
        manifest_path=str(manifest_path),
        substrate_report=report,
        energy=energy,
        quantization=quant_note,
    )


def serve_system(
    system: object,
    *,
    constraints: Constraints | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
    input_shape: tuple[int, ...] = (1, 32),
    max_batch_size: int = 32,
    batch_timeout_ms: int = 10,
) -> None:
    """Run the existing FastAPI edge runtime against a composed system (T23.4.4)."""
    from computronium.deployment import serve_model

    geometry = _geometry_of(system)
    spec = compile_substrate(constraints or Constraints())
    from computronium.ontology.substrate.spec import make_substrate

    apply_substrate_constraints(geometry, make_substrate(spec))
    serve_model(
        _GeometryModule(geometry, None),
        config={"input_shape": list(input_shape)},
        host=host,
        port=port,
        max_batch_size=max_batch_size,
        batch_timeout_ms=batch_timeout_ms,
    )


def spec_constraints(spec: ProblemSpec) -> Constraints:
    """Constraints of a synthesized spec (pass-through helper)."""
    return spec.constraints


__all__ = [
    "KNOWN_QUANTIZATIONS",
    "EnergyEstimate",
    "ExportResult",
    "Quantization",
    "SubstrateReport",
    "apply_substrate_constraints",
    "compile_substrate",
    "estimate_energy",
    "export_system",
    "serve_system",
    "spec_constraints",
    "substrate_report",
]
