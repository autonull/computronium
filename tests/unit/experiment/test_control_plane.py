"""The control plane: the channel the dashboard drives a run through (TODO70).

The plane is the one piece of TODO70 that is architecture rather than chrome,
so these tests are about the properties the rest of the work depends on: the
path is derived by one function, a document written in one process is read in
another, a pause is a boundary and not a kill, a step releases exactly one
batch, a ceiling can be lowered without disturbing the cells in flight, and a
corrupt document never stops a run.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.control import (
    ControlPlane,
    ControlState,
    RunStatus,
    control_plane_path,
)
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.schema import seed_all_registries

pytestmark = pytest.mark.timeout(300)


@pytest.fixture(scope="module", autouse=True)
def _seed_registries() -> None:
    seed_all_registries()


# --------------------------------------------------------------------------
# The path
# --------------------------------------------------------------------------


def test_both_sides_derive_the_same_path(tmp_path: Path) -> None:
    """The plane's path comes from the store's, by one function.

    The dashboard and the run are two processes that must not disagree about
    where the control channel lives. Neither of them knows: both call this.
    """
    store_path = tmp_path / "experiment.duckdb"
    assert control_plane_path(store_path) == control_plane_path(store_path)
    assert control_plane_path(store_path).parent == tmp_path
    assert control_plane_path(store_path).name == "experiment.control.json"
    assert control_plane_path(str(store_path)) == control_plane_path(store_path)


def test_a_pathless_store_gets_a_path_beside_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A store with no path still has a plane, and it is somewhere both sides
    can name.
    """
    monkeypatch.chdir(tmp_path)
    for absent in (None, "", ":memory:"):
        path = control_plane_path(absent)
        assert path.parent == tmp_path
        assert path.name == "experiment.control.json"


# --------------------------------------------------------------------------
# The document
# --------------------------------------------------------------------------


def test_a_plane_written_in_one_process_is_read_in_another(tmp_path: Path) -> None:
    """The channel crosses the process boundary, which is the whole point.

    The writer is a separate interpreter, so this cannot pass by sharing an
    object or a cache: the document itself is the channel.
    """
    path = tmp_path / "experiment.control.json"
    root = Path(__file__).resolve().parents[3]
    writer = (
        "import sys\n"
        f"sys.path.insert(0, {str(root)!r})\n"
        "from computronium.experiment.execution.control import ControlPlane\n"
        f"plane = ControlPlane({str(path)!r})\n"
        "plane.write(paused=True, max_workers=2)\n"
    )
    completed = subprocess.run(
        [sys.executable, "-c", writer],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr

    reader = ControlPlane(path)
    state = reader.read()
    assert state.paused is True
    assert state.max_workers == 2
    assert state.revision == 1


def test_a_corrupt_document_reads_as_not_paused_and_says_why(tmp_path: Path) -> None:
    """A truncated document must not stop a run, and must not lie either.

    The plane reads as "not paused" so a run continues; ``last_error`` says
    why, so the dashboard can say the plane could not be read instead of
    showing a control it cannot honour.
    """
    path = tmp_path / "experiment.control.json"
    path.write_text('{"control": {"paused": tr', encoding="utf-8")

    plane = ControlPlane(path)
    state = plane.read()
    assert state.paused is False
    assert state.revision == 0
    assert plane.last_error is not None


def test_a_write_merges_and_stamps_the_revision(tmp_path: Path) -> None:
    """A write changes what it names and nothing else.

    The revision is what a browser offers back: a stale write is refused
    rather than applied.
    """
    plane = ControlPlane(tmp_path / "experiment.control.json")
    first = plane.write(paused=True)
    assert first.paused is True
    assert first.revision == 1

    second = plane.write(max_workers=8)
    assert second.paused is True, "the write dropped the pause it did not name"
    assert second.max_workers == 8
    assert second.revision == 2


def test_a_step_releases_one_more_batch(tmp_path: Path) -> None:
    """The step budget counts batches released, not presses.

    A step that arrived twice is two batches; a step that was already
    released is not released again.
    """
    plane = ControlPlane(tmp_path / "experiment.control.json")
    assert plane.write(step=True).step_budget == 1
    assert plane.write(step=True).step_budget == 2
    assert plane.write(paused=True).step_budget == 2


def test_the_run_status_survives_a_control_write(tmp_path: Path) -> None:
    """Both halves of the document are written whole, each preserving the other.

    A pause written at the same moment as a status update must not drop
    either: the dashboard's pause and the run's own account of itself are
    two sections of one document.
    """
    path = tmp_path / "experiment.control.json"
    plane = ControlPlane(path)

    plane.write_status(RunStatus(run_id="r1", stage="s6_train", in_flight=2))
    plane.write(paused=True)

    status = ControlPlane(path).read_status()
    assert status is not None
    assert status.run_id == "r1"
    assert status.stage == "s6_train"
    assert status.in_flight == 2


def test_the_document_is_a_json_document_a_reader_can_cat(tmp_path: Path) -> None:
    """The plane is inspectable: what the dashboard asked is on the disk.

    A reader who wants to know what the dashboard told the run does not need
    the dashboard.
    """
    path = tmp_path / "experiment.control.json"
    plane = ControlPlane(path)
    plane.write(paused=True, max_workers=3)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["control"]["paused"] is True
    assert document["control"]["max_workers"] == 3


def test_an_unknown_field_is_refused(tmp_path: Path) -> None:
    """A verb the plane does not have is an error, not a silent no-op."""
    plane = ControlPlane(tmp_path / "experiment.control.json")
    with pytest.raises(ValueError, match="unknown control field"):
        plane.write(turbo=True)


# --------------------------------------------------------------------------
# Waiting
# --------------------------------------------------------------------------


def test_a_waiting_run_holds_until_the_plane_releases_it(tmp_path: Path) -> None:
    """``wait_for_release`` returns when the plane says so, not before."""
    path = tmp_path / "experiment.control.json"
    plane = ControlPlane(path)
    plane.write(paused=True)

    async def scenario() -> str:
        release = asyncio.create_task(plane.wait_for_release())
        await asyncio.sleep(0.1)
        assert not release.done(), "the run was released while the plane held it"
        plane.write(paused=False)
        await asyncio.wait_for(release, timeout=5)
        return "released"

    assert asyncio.run(scenario()) == "released"


def test_a_step_owed_releases_the_run_even_while_paused(tmp_path: Path) -> None:
    """A step is a release, and the plane is still paused afterwards."""
    plane = ControlPlane(tmp_path / "experiment.control.json")
    plane.write(paused=True, step=True)

    async def scenario() -> ControlState:
        return await asyncio.wait_for(plane.wait_for_release(steps_taken=0), timeout=5)

    state = asyncio.run(scenario())
    assert state.paused is True
    assert state.step_budget == 1


# --------------------------------------------------------------------------
# The ceiling
# --------------------------------------------------------------------------


class _BlockingBackend(LocalBackend):
    """A backend whose cells wait for the test to let them finish.

    The ceiling is about admission, so the fixture has to hold cells in
    flight: a backend that answers immediately never has any.
    """

    def __init__(self, *, max_workers: int, expected: int) -> None:
        super().__init__(max_workers=max_workers)
        self.expected = expected
        self.started = 0
        self.all_started = asyncio.Event()
        self.release = asyncio.Event()

    async def submit(self, coordinate, schedule, provenance, params, store):  # type: ignore[no-untyped-def]
        self.started += 1
        if self.started >= self.expected:
            self.all_started.set()
        await self.release.wait()
        return []


def _items(count: int) -> list[tuple[object, object, object, dict[str, object]]]:
    """Cells to admit; the backend never looks inside them."""
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )

    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="euclidean",
        params={},
    )
    schedule = Schedule(
        fidelity="L0", seed=0, n_seeds=1, epochs=1, batch_limit=0, budget_id="test"
    )
    provenance = Provenance(
        env={},
        dataset="digits",
        dataset_version="1.0",
        code_sha="test",
        policy="test",
        links={},
    )
    return [(coordinate, schedule, provenance, {}) for _ in range(count)]


def test_lowering_the_ceiling_leaves_the_cells_in_flight_alone() -> None:
    """The ceiling is a cap, not a kill.

    Lowering it while three cells train must not disturb those three cells:
    they finish, and the next admission waits.
    """
    backend = _BlockingBackend(max_workers=4, expected=3)

    async def scenario() -> None:
        task = asyncio.create_task(backend.submit_batch(_items(3), None))  # type: ignore[arg-type]
        await asyncio.wait_for(backend.all_started.wait(), timeout=5)
        assert backend.in_flight == 3
        await backend.set_max_workers(1)
        assert backend.in_flight == 3, "the cells in flight were disturbed"
        backend.release.set()
        await asyncio.wait_for(task, timeout=5)

    asyncio.run(scenario())


def test_raising_the_ceiling_admits_the_cells_that_waited() -> None:
    """A ceiling that only falls would starve a run the reader wants faster."""
    backend = _BlockingBackend(max_workers=1, expected=2)

    async def scenario() -> None:
        task = asyncio.create_task(backend.submit_batch(_items(2), None))  # type: ignore[arg-type]
        await asyncio.sleep(0.05)
        assert backend.in_flight == 1, "the ceiling admitted more than it allowed"
        await backend.set_max_workers(2)
        await asyncio.wait_for(backend.all_started.wait(), timeout=5)
        assert backend.in_flight == 2
        backend.release.set()
        await asyncio.wait_for(task, timeout=5)

    asyncio.run(scenario())


# --------------------------------------------------------------------------
# The run reads the plane
# --------------------------------------------------------------------------


def _runner(tmp_path: Path, plane_path: Path) -> PipelineRunner:
    """A runner over the mechanism lock's declaration, with a control plane."""
    from computronium.experiment.evidence import RecordStore, StoreConfig
    from computronium.experiment.execution import (
        Budget,
        SimpleCostModel,
        StratifiedRandomPolicy,
    )
    from tests.property._specs import mechanism_spec

    spec = mechanism_spec()
    store = RecordStore(StoreConfig(path=tmp_path / "controlled.duckdb"))
    store.__enter__()
    run_id = store.create_run(spec=spec)
    config = PipelineConfig(
        run_id=run_id,
        run_spec=spec,
        budget=Budget.from_duration("10m"),
        cost_model=SimpleCostModel(),
        backend=LocalBackend(max_workers=2),
        policy=StratifiedRandomPolicy(seed=7),
        max_rounds=1,
        control_plane=plane_path,
    )
    return PipelineRunner(config, store)


def _with_backend(runner: PipelineRunner, backend: object) -> None:
    """Swap the runner's backend for one the test can watch."""
    import dataclasses

    runner._config = dataclasses.replace(runner._config, backend=backend)  # type: ignore[arg-type]


def test_a_paused_plane_holds_the_run_at_a_boundary(tmp_path: Path) -> None:
    """A pause takes effect at a boundary and not before.

    The run must not have measured anything while the plane holds it, and it
    must measure once the plane releases it.
    """
    from tests.property._fake_backend import FakeBackend

    plane_path = tmp_path / "experiment.control.json"
    plane = ControlPlane(plane_path)
    plane.write(paused=True)

    runner = _runner(tmp_path, plane_path)
    backend = FakeBackend()
    _with_backend(runner, backend)

    async def scenario() -> None:
        task = asyncio.create_task(runner.run())
        await asyncio.sleep(0.3)
        assert backend.submitted == [], "the run measured while the plane held it"
        plane.write(paused=False)
        await asyncio.wait_for(task, timeout=60)

    asyncio.run(scenario())
    assert backend.submitted, "the run measured nothing once released"


def test_a_corrupt_plane_does_not_stop_a_run(tmp_path: Path) -> None:
    """A truncated document must not stop a run.

    The plane reads as "not paused", so the run proceeds: a dashboard that
    died mid-write must not take the run down with it.
    """
    from tests.property._fake_backend import FakeBackend

    plane_path = tmp_path / "experiment.control.json"
    plane_path.write_text("{not json", encoding="utf-8")

    runner = _runner(tmp_path, plane_path)
    backend = FakeBackend()
    _with_backend(runner, backend)
    asyncio.run(asyncio.wait_for(runner.run(), timeout=60))
    assert backend.submitted, "a corrupt plane stopped the run"


def test_the_run_publishes_what_it_is_doing(tmp_path: Path) -> None:
    """The dashboard reads the run's counters from the same document.

    A run in another process cannot be asked what it is doing over a socket
    it does not own, so it says so on the plane.
    """
    from tests.property._fake_backend import FakeBackend

    plane_path = tmp_path / "experiment.control.json"
    runner = _runner(tmp_path, plane_path)
    backend = FakeBackend()
    _with_backend(runner, backend)
    asyncio.run(asyncio.wait_for(runner.run(), timeout=60))

    status = ControlPlane(plane_path).read_status()
    assert status is not None, "the run published no status"
    assert status.run_id == runner._config.run_id
    assert status.stage
    assert status.cells_done == len(backend.submitted)
