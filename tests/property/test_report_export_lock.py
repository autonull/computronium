"""W64: the report's export and stability paths, locked on what they decide.

``surface/report.py`` was half covered after the front and render locks: the
LaTeX/PDF export and the dynamical-stability section were the untouched mass.
Each is a decision, so each is asserted directly (D6):

* **A report is a document, and the run id is data inside it.** A run id that
  carries LaTeX syntax (``_``, ``&``) is escaped, not interpreted; the same
  text is the file's title and the run's records.
* **A missing run is refused by name**, not rendered as an empty report.
* **A missing conversion tool is an environment refusal by name**, not a
  traceback; a failed conversion names the converter's own error.
* **The intermediate LaTeX file is removed unless the caller keeps it.**
* **Stability analysis appears only when a record carries a stability
  metric**, so a task without one renders no stability section.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.schema import (
    Coordinate,
    FailureCause,
    GateVerdict,
    Maturity,
    Provenance,
    Record,
    ReproducibilityClass,
    Schedule,
    Severity,
    Status,
)
from computronium.experiment.surface.report import (
    generate_html_report,
    generate_latex_report,
    generate_pdf_report,
)

_RECORDS = 3


def _record(run_id: str, seed: int, payload: dict[str, Any] | None = None) -> Record:
    return Record.create(
        run_id=run_id,
        coordinate=Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={"hidden_dims": 16},
        ),
        schedule=Schedule(
            fidelity="L1",
            seed=seed,
            n_seeds=1,
            epochs=1,
            batch_limit=2,
            budget_id="b",
            task_id="digits",
        ),
        provenance=Provenance(
            env={"python": "3.14", "platform": "test"},
            dataset="digits",
            dataset_version="1.0",
            code_sha="test",
            policy="test",
            links={"run_id": run_id},
        ),
        status=Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L1,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload=payload
        or {
            "val_acc": 0.8 + 0.02 * seed,
            "walltime_total": 12.0,
            "param_count": 1600,
            "train_acc": 0.9,
        },
    )


@pytest.fixture
def store() -> Any:
    with RecordStore(StoreConfig(path=Path(":memory:"))) as opened:
        yield opened


def _run(store: RecordStore, run_id: str = "run_a&b") -> str:
    store.create_run(run_id=run_id)
    for seed in range(_RECORDS):
        store.append(_record(run_id, seed))
    return run_id


def test_a_latex_report_is_a_document_that_escapes_the_run_id(
    store: RecordStore, tmp_path: Path
) -> None:
    run_id = _run(store)

    path = generate_latex_report(store, run_id, tmp_path / "report.tex")
    text = path.read_text(encoding="utf-8")

    assert text.startswith(r"\documentclass")
    assert text.rstrip().endswith(r"\end{document}")
    assert r"\title{Computronium Run Report: run\_a\&b}" in text
    assert r"\section{Run Summary}" in text
    assert f"Total Records & {_RECORDS}" in text


def test_a_latex_report_refuses_a_run_that_does_not_exist(
    store: RecordStore, tmp_path: Path
) -> None:
    _run(store)

    with pytest.raises(ValueError, match="absent"):
        generate_latex_report(store, "absent", tmp_path / "report.tex")


def test_pdf_export_refuses_by_name_when_the_converter_is_missing(
    store: RecordStore, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = _run(store)
    monkeypatch.setattr(shutil, "which", lambda _name: None)

    with pytest.raises(RuntimeError, match="pandoc"):
        generate_pdf_report(store, run_id, tmp_path / "report.pdf")


def test_pdf_export_names_the_converter_failure(
    store: RecordStore, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = _run(store)
    monkeypatch.setattr(shutil, "which", lambda _name: "/usr/bin/pandoc")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="tex engine missing"
        ),
    )

    with pytest.raises(RuntimeError, match="tex engine missing"):
        generate_pdf_report(store, run_id, tmp_path / "report.pdf")


def test_pdf_export_removes_the_intermediate_latex_unless_kept(
    store: RecordStore, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = _run(store)
    monkeypatch.setattr(shutil, "which", lambda _name: "/usr/bin/pandoc")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        ),
    )

    transient = generate_pdf_report(store, run_id, tmp_path / "transient.pdf")
    assert transient == tmp_path / "transient.pdf"
    assert not (tmp_path / "transient.tex").exists()

    kept = generate_pdf_report(store, run_id, tmp_path / "kept.pdf", keep_tex=True)
    assert kept == tmp_path / "kept.pdf"
    assert (tmp_path / "kept.tex").exists()


def _stability_run(store: RecordStore) -> str:
    run_id = store.create_run()
    for seed in range(_RECORDS):
        store.append(
            _record(
                run_id,
                seed,
                payload={
                    "val_acc": 0.8,
                    "walltime_s": 12.0,
                    "lyapunov_exponent": 0.01 * (seed + 1),
                    "spectral_radius": 0.9,
                    "max_singular_value": 1.0,
                    "settle_steps": 10,
                },
            )
        )
    return run_id


def test_the_html_report_renders_stability_when_a_record_carries_it(
    store: RecordStore, tmp_path: Path
) -> None:
    run_id = _stability_run(store)

    page = generate_html_report(store, run_id, tmp_path / "report.html").read_text(
        encoding="utf-8"
    )

    assert "Dynamical Stability Analysis" in page
    assert "Lyapunov Exponent Distribution" in page
    assert "Spectral Radius vs Max Singular Value" in page


def test_the_html_report_omits_stability_when_no_record_carries_it(
    store: RecordStore, tmp_path: Path
) -> None:
    run_id = _run(store)

    page = generate_html_report(store, run_id, tmp_path / "report.html").read_text(
        encoding="utf-8"
    )

    assert "Dynamical Stability Analysis" not in page
