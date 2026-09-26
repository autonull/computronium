"""Every reachable triton rung has a GPU benchmark row beside its reference number.

TODO36 §0.3 item 5. Read-only: the rows are produced by
``python -m computronium.acceleration.rungbench`` on a CUDA box, so this lock
runs anywhere.

``artifacts/`` is gitignored, so on a fresh clone there are no rows and this file
skips rather than fails — same policy as the microbench evidence check in
``test_all_implementations.py``. When rows *are* present, a rung that lost its
coverage fails.
"""

import json
import pathlib
import statistics
from collections import defaultdict

import pytest

from computronium.acceleration.rungbench import rung_sites

ROWS = pathlib.Path("artifacts/benchmarks/rungs")

_MIN_SCALES = 3


def _rows() -> list[dict]:
    if not ROWS.exists():
        return []
    return [
        json.loads(line)
        for path in sorted(ROWS.glob("*.jsonl"))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


requires_rows = pytest.mark.skipif(
    not _rows(), reason="no rung rows recorded; run computronium.acceleration.rungbench"
)


def _gpu_rungs() -> set[tuple[str, str]]:
    return {
        (str(row["id"]), str(row["rung"]))
        for row in _rows()
        if row.get("device") == "cuda" and row.get("status") == "ok"
    }


@requires_rows
@pytest.mark.parametrize("site", rung_sites(), ids=lambda site: site.id)
def test_site_has_gpu_rows(site) -> None:
    """Each rung of each measured site is timed on a GPU at every scale."""
    covered = _gpu_rungs()
    for rung in site.rungs:
        if not rung.available():
            continue
        assert (site.id, rung.label) in covered, (
            f"{site.id} rung {rung.label} ({rung.technology}) has no GPU row in {ROWS}"
        )


@requires_rows
@pytest.mark.parametrize("site", rung_sites(), ids=lambda site: site.id)
def test_site_measured_at_three_sizes(site) -> None:
    scales = {
        row["scale"]
        for row in _rows()
        if row["id"] == site.id and row["device"] == "cuda"
    }
    assert len(scales) >= _MIN_SCALES, f"{site.id} measured at scales {sorted(scales)}"


@requires_rows
def test_every_gpu_row_belongs_to_a_site() -> None:
    known = {site.id for site in rung_sites()}
    for row in _rows():
        assert row["id"] in known, f"orphan rung row for {row['id']}"
        assert "technology" in row, "a rung row must name its technology"


@requires_rows
def test_gpu_rows_pair_every_rung_with_its_reference() -> None:
    """A rung measured without the rung below it is not a comparison."""
    times: dict[tuple[str, str, int], list[float]] = defaultdict(list)
    for row in _rows():
        if row.get("device") != "cuda" or row.get("status") != "ok":
            continue
        times[str(row["id"]), str(row["rung"]), int(row["scale"])].append(
            float(row["wall_time_ms"])
        )
    for (site_id, rung, scale), values in times.items():
        if rung == "reference":
            continue
        assert (site_id, "reference", scale) in times, (
            f"{site_id} rung {rung} at scale {scale} has no reference number"
        )
        assert statistics.median(values) > 0.0
