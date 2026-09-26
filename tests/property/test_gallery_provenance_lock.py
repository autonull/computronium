"""§2.6: a run record's provenance must survive the run that produced it.

Two defects, both invisible until the provenance was read rather than
assumed:

* **The emitter ran git in the demo's cwd.** `emit_run_record` shells out to
  `git rev-parse HEAD` with no `cwd`, and demos that `monkeypatch.chdir` into
  a tmp_path first run it outside any work tree. The handler caught the
  failure and recorded the string ``"unknown"``, so the record looked
  complete and carried no provenance at all. `d24_evolution_search.json` had
  been sitting that way since `b5a1ff1b`. Fixed by pinning `cwd` to the repo
  root; this lock is what makes the fix permanent, and it is why "the handler
  has a fallback" is not the same as "the value is right".
* **`config_sha256` is a hash of the data, not of the config.** The key name
  promises exactly the provenance §2.6 wants -- so a future drift lock will
  reach for it to answer "did the configuration change?" and get a hash that
  only moves when the *numbers* move. A different emitter in the repo
  (`experiments/joint/z3_fixed_weights.py`) uses the same key name for a
  genuine config hash, so the two conventions already collide. Asserted here
  so the name cannot be taken at face value by the next reader.

This lock is deliberately in the fast lane and reads the *committed* records.
`tests/integration/test_gallery_lock.py` validates freshly-emitted records
after the demos run, which is a round-close concern; provenance that silently
decays between round closes needs a per-commit gate.

Not covered, and the reason this file is not the whole of §2.6: an
environment fingerprint (torch/CUDA/python versions). The machinery already
exists -- `computronium.utils.capture_environment()` and `deps_hash()` -- but
backfilling it means re-emitting every record, i.e. re-running every demo, and
hand-editing a version string into a record would be fabricating provenance
rather than recording it. That belongs with §1.6's slow pass.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

from computronium.visualization.gallery import canonicalize_floats

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS_DIR = REPO_ROOT / "docs" / "figures" / "run_records"

PROVENANCE_KEYS = {"git_commit", "config_sha256"}
_SHA = re.compile(r"[0-9a-f]{40}")


def _records() -> dict[str, dict]:
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(RECORDS_DIR.glob("*.json"))
    }


def test_the_scan_actually_scans() -> None:
    """A lock over zero records is a lock that cannot fail (§0.6)."""
    assert len(_records()) >= 25, "run records went missing or were renamed"


@pytest.mark.parametrize("name", sorted(_records()))
def test_record_names_a_real_ancestor_commit(name: str) -> None:
    """`git_commit` must be a commit this repository can still reach.

    A record whose commit is absent, or not an ancestor of HEAD, was emitted
    from another clone, another branch, or a tree that no longer exists -- and
    the figure it pins cannot be traced to any code in this history.
    """
    commit = _records()[name]["provenance"]["git_commit"]
    assert _SHA.fullmatch(commit), (
        f"{name}: provenance records {commit!r} rather than a commit sha; "
        "the emitter's git call is failing (cwd outside the repo?)"
    )
    reachable = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=REPO_ROOT,
        check=False,
    )
    assert reachable.returncode == 0, (
        f"{name}: emitted at {commit[:8]}, which is not an ancestor of HEAD; "
        "re-emit the demo so the record points at reachable history"
    )


@pytest.mark.parametrize("name", sorted(_records()))
def test_provenance_keys_are_exactly_the_emitter_contract(name: str) -> None:
    """A provenance field the lock does not read is a field nobody checks."""
    assert set(_records()[name]["provenance"]) == PROVENANCE_KEYS


@pytest.mark.parametrize("name", sorted(_records()))
def test_config_sha256_hashes_the_data_not_the_config(name: str) -> None:
    """Pin the misleading name before someone builds on it (§2.6).

    `config_sha256` is the sha256 of the canonicalised `data` payload, so it
    moves when the numbers move and not when the configuration does. It is a
    tamper check, and it is the only thing in the record that is.
    """
    record = _records()[name]
    data_sha = hashlib.sha256(
        json.dumps(
            canonicalize_floats(record["data"]),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    assert record["provenance"]["config_sha256"] == data_sha, (
        f"{name}: config_sha256 is documented as a hash of the canonicalised "
        "data payload; if this now differs, the emitter's convention changed "
        "and every record's provenance needs re-examining"
    )
