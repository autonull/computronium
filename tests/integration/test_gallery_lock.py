"""Figure lock with teeth (TODO10 R10.1.4).

The gallery cannot silently drift from what the code actually demonstrates.
The data layer of every demo run record (recorded metric values, not
pixels) is checksummed into the committed manifest; this test regenerates
the gallery and compares. A mismatch means one of two things, both caught:
the code changed what it demonstrates (review the diff, re-pin the manifest
deliberately) or the demo became nondeterministic (a bug — fix it).

Runs after the demo tests (alphabetical file order in this directory), so
the records on disk are from the same gate run.
"""

import hashlib
import json
from pathlib import Path

from computronium.visualization.gallery import (
    DEMOS,
    canonicalize_floats,
    render_gallery,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = REPO_ROOT / "docs" / "figures"
RECORDS_DIR = FIGURES_DIR / "run_records"

# Single-source demo registry (R1.3): the lock's expectation table is
# derived from `DEMOS` so a new demo is one registry row + a re-pin.
EXPECTED = {name: spec.capability_id for name, spec in DEMOS.items()}


def _records() -> dict[str, dict]:
    records: dict[str, dict] = {}
    for path in sorted(RECORDS_DIR.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        records[record["capability_name"]] = record
    return records


def _git_head() -> str:
    import subprocess  # ruff: ignore[suspicious-subprocess-import] (fixed arg list, no shell)

    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def test_g_axis_demos_record_param_counts() -> None:
    """Any demo whose registry entry declares a G-axis comparison must
    carry ``param_counts`` for every arm — capacity mismatches cannot
    hide in the figure (TODO17 §3.2)."""
    records = _records()
    for name, spec in DEMOS.items():
        if not spec.g_axis:
            continue
        counts = records.get(name, {}).get("data", {}).get("param_counts")
        assert counts, f"{name}: G-axis demo missing param_counts"


def test_figure_lock(tmp_path: Path) -> None:
    records = _records()
    assert set(records) == set(EXPECTED), (
        f"missing demo records: {sorted(set(EXPECTED) - set(records))}"
    )

    for name, record in records.items():
        assert (REPO_ROOT / record["demo_test"]).exists(), (
            f"stale record for {name}: demo test deleted, claim must retire"
        )
        data_sha = hashlib.sha256(
            json.dumps(
                canonicalize_floats(record["data"]),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        assert data_sha == record["provenance"]["config_sha256"], (
            f"record for {name} was tampered with or the emitter changed"
        )

    metas = render_gallery(RECORDS_DIR, tmp_path)
    assert {m.capability_name for m in metas} == set(EXPECTED)

    manifest = json.loads((FIGURES_DIR / "manifest.json").read_text(encoding="utf-8"))
    pinned = {f["capability_name"]: f for f in manifest["figures"]}
    assert set(pinned) == set(EXPECTED), "manifest has orphaned or missing capabilities"
    for name, entry in pinned.items():
        fresh = next(m for m in metas if m.capability_name == name)
        assert entry["data_sha256"] == fresh.data_sha256, (
            f"figure data for {name} drifted from the pinned manifest — "
            f"review the demo diff, then re-pin deliberately "
            f"(record emitted at {record['provenance']['git_commit'][:8]}, "
            f"HEAD is {_git_head()[:8]}; if the emitting commit predates the "
            "demo's last change, the record is stale — run the demo "
            "(slow demos need -m slow) and re-pin)"
        )
        assert entry["demo_test"] == fresh.demo_test
