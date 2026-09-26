"""The reduction order of an emitted record is pinned, and named in it.

`tests/conftest.py` carried `os.environ.setdefault("OMP_NUM_THREADS", "1")`
until this commit. It sat *below* that file's own `import torch`, where it
does nothing: OpenMP reads the variable once, at import, and the suite ran at
8 threads the whole time. A dead line that reads as a determinism guarantee
is the defect class TODO35 §10.2 is about — a claim nothing was checking.

What a pin is worth is measured, not assumed
(`scripts/probes/todo35_d16_determinism.py`): a seeded CPU demo arm is
bit-identical across processes at a fixed thread count, and differs by ~1e-4
in accuracy between 1 and 8. Seeding the RNG is necessary and not sufficient
for a run record to mean anything; the reduction order has to be pinned too.

The pin is in `tests/integration/conftest.py` — the tier that emits records —
because pinning the environment for the whole suite cost the fast lane 96s →
186s for a guarantee only those records need. Three assertions:

* the pin exists, and it is a runtime `torch.set_num_threads` in a module
  whose import order cannot matter (the failure the old line had);
* every committed record names the pinned count, so a record emitted before
  the pin existed is distinguishable from one emitted under it;
* the count is 1, and the scan found exactly one pinning module — a second
  pin elsewhere would make two tiers' records incomparable.
"""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS_DIR = REPO_ROOT / "docs" / "figures" / "run_records"
EMITTER_CONFTEST = REPO_ROOT / "tests" / "integration" / "conftest.py"
MIN_RECORDS = 25


def _emitter_conftest() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_emitter_conftest", EMITTER_CONFTEST)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _records() -> dict[str, dict]:
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(RECORDS_DIR.glob("*.json"))
    }


def test_the_scan_actually_scans() -> None:
    """A lock over zero records cannot fail (§0)."""
    assert len(_records()) >= MIN_RECORDS, (
        "run records went missing or were renamed; the thread-count lock now "
        "has no population"
    )


def test_exactly_one_module_pins_the_reduction_order() -> None:
    """Two pins, two sets of records, and no way to tell them apart."""
    pins: list[Path] = []
    for path in sorted(REPO_ROOT.glob("**/conftest.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "set_num_threads"
            for node in ast.walk(tree)
        ):
            pins.append(path)
    assert pins == [EMITTER_CONFTEST], (
        f"reduction-order pins found in {[p.name for p in pins]}; exactly one "
        f"module may pin, and it is {EMITTER_CONFTEST.relative_to(REPO_ROOT)}"
    )


def test_the_pin_is_a_runtime_call_not_an_environment_variable() -> None:
    """`OMP_NUM_THREADS` is read once, at import. A late setdefault is a no-op.

    This is the whole defect: the pin existed for months in a form that could
    not work, in a file that imports torch above it.
    """
    tree = ast.parse(EMITTER_CONFTEST.read_text(encoding="utf-8"))
    env_pins = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "setdefault"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value in {"OMP_NUM_THREADS", "MKL_NUM_THREADS"}
    ]
    assert not env_pins, (
        "the emitter conftest sets a thread environment variable; that only "
        "works if it runs before torch is imported, which a conftest cannot "
        "guarantee — use the runtime set_num_threads the fixture already has"
    )


@pytest.mark.parametrize("name", sorted(_records()))
def test_record_names_the_pinned_thread_count(name: str) -> None:
    """The count is a precondition of every number in the record.

    A record emitted before the pin existed carries 8 (or nothing at all), and
    is not comparable with one emitted under it — which is the drift
    TODO35 §10.3 could see and could not diagnose.
    """
    pinned = _emitter_conftest().PINNED_THREADS
    emitted = _records()[name]["provenance"].get("torch_threads")
    assert emitted == pinned, (
        f"{name}: emitted at {emitted!r} torch threads, the pin is {pinned}; "
        "re-emit it (slow tier) or its numbers are not comparable with the "
        "rest of the gallery"
    )
