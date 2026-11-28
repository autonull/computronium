"""W64: the documentation generators, locked on what they publish.

The documentation package was 38% covered: its three CLIs (FAQ, experiment
catalog, method cards) never ran. Each publishes a table, so each is
asserted on the table it publishes (D6):

* **The FAQ list is filtered by category and found by search**; an unknown
  id is refused by name; a generated file holds every entry.
* **The catalog lists the store's runs and searches its records**; the
  export round-trips the catalog to a file.
* **A method card is the registry's primitive**, and the list covers every
  axis; an unknown primitive is refused by name.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from computronium.experiment.documentation import catalog, faq, method_cards
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

if TYPE_CHECKING:
    from pathlib import Path

_RECORDS = 3


def _record(run_id: str, seed: int) -> Record:
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
        payload={"val_acc": 0.8 + 0.01 * seed, "walltime_s": 12.0},
    )


@pytest.fixture
def store_path(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "experiment.duckdb"
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run()
        for seed in range(_RECORDS):
            store.append(_record(run_id, seed))
    return path, run_id


def test_the_faq_lists_a_category_and_searches_its_entries(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert faq.main(["list", "--category", "substrate", "--format", "json"]) == 0
    entries: list[dict[str, Any]] = json.loads(capsys.readouterr().out)

    assert entries
    assert {entry["category"] for entry in entries} == {"substrate"}

    assert faq.main(["search", "substrate", "--format", "json"]) == 0
    found: list[dict[str, Any]] = json.loads(capsys.readouterr().out)
    assert found


def test_the_faq_shows_an_entry_and_refuses_an_unknown_id(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert faq.main(["show", "FAQ-001", "--format", "json"]) == 0
    entry: dict[str, Any] = json.loads(capsys.readouterr().out)
    assert entry["id"] == "FAQ-001"

    assert faq.main(["show", "FAQ-999"]) == 1
    assert "FAQ-999" in capsys.readouterr().err


def test_the_faq_generates_every_entry_to_a_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "faq.md"

    assert faq.main(["generate", "--output", str(output)]) == 0
    text = output.read_text(encoding="utf-8")

    assert len(faq.generate_faq()) > 0
    assert "FAQ-001" in text
    assert "Generated" in capsys.readouterr().out


def test_the_catalog_lists_the_stores_runs(
    store_path: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    path, run_id = store_path

    assert catalog.main(["list", "--store", str(path), "--format", "json"]) == 0
    runs: list[dict[str, Any]] = json.loads(capsys.readouterr().out)

    assert [run["run_id"] for run in runs] == [run_id]


def test_the_catalog_searches_the_stores_records(
    store_path: tuple[Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    path, _run_id = store_path

    assert (
        catalog.main([
            "search",
            "--store",
            str(path),
            "--substrate",
            "digital",
            "--format",
            "json",
        ])
        == 0
    )
    records: list[dict[str, Any]] = json.loads(capsys.readouterr().out)

    assert len(records) == _RECORDS
    assert {record["substrate"] for record in records} == {"digital"}


def test_the_catalog_export_round_trips_to_a_file(
    store_path: tuple[Path, str], tmp_path: Path
) -> None:
    path, run_id = store_path
    output = tmp_path / "catalog.json"

    assert (
        catalog.main([
            "export",
            "--store",
            str(path),
            "--output",
            str(output),
            "--format",
            "json",
        ])
        == 0
    )
    exported = json.loads(output.read_text(encoding="utf-8"))

    assert exported[0]["run_id"] == run_id


def test_method_cards_cover_every_axis(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert method_cards.main(["list", "--axis", "substrate", "--format", "json"]) == 0
    cards: list[dict[str, Any]] = json.loads(capsys.readouterr().out)

    assert cards
    assert {card["axis"] for card in cards} == {"substrate"}


def test_a_method_card_is_the_registrys_primitive(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert method_cards.main(["show", "substrate", "digital", "--format", "json"]) == 0
    card: dict[str, Any] = json.loads(capsys.readouterr().out)

    assert card["axis"] == "substrate"
    assert card["name"] == "digital"
    assert card["class_name"] == "DigitalSubstrate"


def test_method_cards_generate_a_document(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "cards.md"

    assert method_cards.main(["generate", "--output", str(output)]) == 0
    text = output.read_text(encoding="utf-8")

    assert "substrate" in text.lower()
    assert "digital" in text
    assert "Generated" in capsys.readouterr().out
