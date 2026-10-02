"""T21.3A.7 lab boundary: computronium-lab is the sanctioned integration layer.

Direction: lab MAY import computronium (that is its job — preset factories
over the ontology); computronium and the standalone packages must NOT
import computronium_lab. Decision recorded in PLATFORM_LAUNCH.md.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.append(node.module)
    return names


def _imported_root_modules(path: Path) -> list[str]:
    return [name.split(".")[0] for name in _imported_modules(path)]


_SRC = Path(__file__).resolve().parents[1] / "src" / "computronium_lab"


def test_lab_may_import_computronium() -> None:
    src = Path(__file__).resolve().parents[1] / "src"
    assert any(
        "computronium" in _imported_root_modules(p) for p in src.rglob("*.py")
    ), "lab must integrate computronium (sanctioned direction)"


def test_nothing_imports_the_lab() -> None:
    offenders: list[str] = []
    targets = [REPO_ROOT / "computronium"] + [
        d / "src"
        for d in (REPO_ROOT / "packages").iterdir()
        if d.name != "computronium-lab"
    ]
    for base in targets:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if "computronium_lab" in _imported_root_modules(path):
                offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, f"forbidden computronium_lab imports: {offenders}"


def test_exploratory_synthesis_records_ceec(tmp_path):
    from computronium_lab import Constraints, Lab

    class LowConfidenceModel:
        """Fixed below LOW_CONFIDENCE: the ingestion path's own fixture.

        The shared fitted model crossed the 0.7 threshold for this spec's
        catalog (ff_mlp predicts 0.749), which silently retired the
        exploratory branch (TODO47 §1.4) — the gate now pins the prediction
        instead of inheriting a fit's drift.
        """

        @staticmethod
        def predict(_features: object) -> float:
            return 0.5

        @staticmethod
        def rationale(_features: object) -> str:
            return "fixture: fixed low-confidence prediction"

    ledger = tmp_path / "ledger.db"
    lab = Lab(seed=0, record_ledger=str(ledger))
    spec = lab.specify(
        "classification",
        "synthetic",
        constraints=Constraints(substrate="digital", latency_ms=5.0),
    )
    result = lab.synthesize(spec, model=LowConfidenceModel())
    assert result.exploratory
    artifacts = sorted((tmp_path / "artifacts").glob("*"))
    assert artifacts, "exploratory synthesis must ingest a CEEC artifact"
    import sqlite3

    conn = sqlite3.connect(ledger)
    types = [t for (t,) in conn.execute("SELECT type FROM artifacts").fetchall()]
    conn.close()
    assert "exploratory_synthesis" in types, types


def test_lab_extracts_measured_metrics_through_the_kernel() -> None:
    """The lab's measured metrics come from the kernel's one extraction.

    A second history→metrics filter is how the lab's dead fallback keys
    (``free_accuracy``/``loss`` never occur in a trainer history row) hid
    from themselves — TODO47 T6. ``train_with_certificates`` is the lab's
    single measured-metric producer; it must consume the kernel's
    ``history_metrics`` rather than re-implement it.
    """
    tree = ast.parse((_SRC / "training.py").read_text(encoding="utf-8"))
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.level == 0
        and node.module == "computronium.experiment.execution.evaluate"
        for alias in node.names
    }
    assert "history_metrics" in imported, imported


def test_lab_never_touches_the_claim_surface() -> None:
    """The lab's predicted metrics cannot enter a claim: no store, no claims.

    ``Lab.explore`` returns a frontier of *predicted* viability from a static
    catalog (TODO46 §D9); those numbers only stay honest if they cannot reach
    the kernel's record store or claim derivation, which speak only in
    measured records.
    """
    forbidden = (
        "computronium.experiment.evidence.store",
        "computronium.experiment.evidence.claims",
    )
    offenders = [
        f"{path.relative_to(_SRC)} -> {name}"
        for path in _SRC.rglob("*.py")
        for name in _imported_modules(path)
        if name in forbidden
    ]
    assert not offenders, offenders


def test_predicted_fields_are_named_predicted() -> None:
    """Every prediction the synthesis surface carries says ``predicted_``.

    ``ComparisonResult.final_accuracy`` is *measured* (Lab.train) and is
    correctly not covered — the lock speaks to what the catalog predicts.
    """
    import dataclasses

    from computronium_lab.synthesis.engine import ParetoOption, SynthesisResult

    for obj in (SynthesisResult, ParetoOption):
        for field in dataclasses.fields(obj):
            if "viability" in field.name or "accuracy" in field.name:
                assert field.name.startswith("predicted_"), (
                    f"{obj.__name__}.{field.name} is a prediction without "
                    "the predicted_ label"
                )
