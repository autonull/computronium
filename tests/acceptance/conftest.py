"""One campaign run, one store, every consumer (TODO48b R8).

Four gates need the §3.6 campaign: D3's owed verification (round loop, budget,
record identity), E3 (the report names the control), CP-1 (declared records ==
stored records, walltime inside D2's projection, claims with uncertainty), and
F2 (every README pipeline number traces here). Before this fixture each of them
ran the campaign in its own module, so a session paid the same ~150 s four
times and no two gates ever read the same measurement.

**The fixture is session-scoped and cross-worker, and both facts are load-bearing.**
``addopts`` carries ``-n 4``, and an xdist worker is a separate process with its
own module-scope: a module-scoped fixture runs *once per worker*, so the first
draft of this file paid the campaign **twice** for two modules and timed out at
300 s each. Measured, in the run that found it: seven passes, eleven setup
timeouts, 698 s.

So the store lives at a path *derived from the declaration*, not from the
test's tmpdir, and a file lock makes exactly one process build it while the
others wait and then read the same store. Two consumers in two workers now read
one measurement; that is the whole saving this ticket exists to collect.

The run goes through the command surface (``comp run``), because a gate stated
against a Python API proves the API and not the command.

Cost discipline: the campaign is a normal test because one cell was measured,
not assumed. At the measured regime a cell is ~0.5 s of *serial* work, the
space holds 90 legal cells over 5 seeds (450 records), and the run executes its
batches 4-way concurrent — measured 232 s wall for the whole space. If it grows
past ~5 minutes, re-price it and move this to the demo tier rather than letting
the default shard absorb it.
"""

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path

import pytest
from _campaign import CAMPAIGN, Campaign
from filelock import FileLock

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.surface import cli

# The fixture is shared across four modules *and* four workers, so the 900 s
# ``test_campaign_lock.py`` allows must cover the run plus every gate reading it.
pytestmark = pytest.mark.timeout(1800)

_PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "computronium"


def _store_dir() -> Path:
    """Where this session's campaign store lives, shared by every worker.

    Keyed by the declaration *and the code*, because a store is the output of
    both: keying on the spec alone let this session's own E3 fix read a store
    built before it, and the three failing gates said so. Two workers that
    agree on both agree on the path, which is the property the lock needs.

    ``hash()`` is process-salted and useless across workers, hence the digest.
    """
    root = Path(os.environ.get("COMPUTRONIUM_CAMPAIGN_STORE", ".pytest_cache/campaign"))
    canonical = RunSpec.load(CAMPAIGN).model_dump_json()
    fingerprint = f"{canonical}|{_code_fingerprint()}"
    return root / hashlib.sha256(fingerprint.encode()).hexdigest()[:16]


def _code_fingerprint() -> str:
    """A cheap identity for the package under test: its newest source mtime.

    Git was tried first and is *wrong here*, which is worth recording: HEAD plus
    a dirty flag does not change when an already-dirty file is edited, so a
    store built before a fix survived it — measured, three gates reading a store
    from the code they were meant to be testing. A gate's cache key must change
    on every edit, and the filesystem's own answer is the only one that does
    without a VCS round-trip per worker.
    """
    newest = max(
        (path.stat().st_mtime_ns for path in _PACKAGE_ROOT.rglob("*.py")),
        default=0,
    )
    return f"mtime-{newest}"


@pytest.fixture(scope="session")
def campaign() -> Campaign:
    """Run the campaign once per session; hand every gate the same store."""
    seed_all_registries()
    directory = _store_dir()
    directory.mkdir(parents=True, exist_ok=True)
    store_path = directory / "campaign.duckdb"
    timing_path = directory / "elapsed_s"
    lock_path = directory / "run.lock"

    with FileLock(str(lock_path)):
        if timing_path.exists() and store_path.exists():
            elapsed = float(timing_path.read_text(encoding="utf-8"))
        else:
            started = time.monotonic()
            assert (
                cli.main(["run", "--spec", str(CAMPAIGN), "--store", str(store_path)])
                == 0
            )
            elapsed = time.monotonic() - started
            timing_path.write_text(str(elapsed), encoding="utf-8")

    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        run = store.query_runs()[0]
        return Campaign(
            spec=RunSpec.load(CAMPAIGN),
            store_path=store_path,
            run_id=run.run_id,
            status=run.status,
            replay_hash=run.replay_hash or "",
            budget_consumed_s=run.budget_consumed_s or 0.0,
            elapsed_s=elapsed,
            records=tuple(store.query_records(run_id=run.run_id)),
        )
