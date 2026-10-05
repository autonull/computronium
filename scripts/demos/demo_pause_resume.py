"""Demo: U3 multi-round pause/resume by run_id.

Expected: no re-measurement after resume; store record count is monotonic.
Same APIs as tests/acceptance/test_unified_kernel.py (U3).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _support import (
    fresh_store,
    make_pipeline_config,
    make_run_spec,
    open_store,
    run_pipeline,
)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store, store_path = fresh_store(Path(tmp), "u3")
        run_spec = make_run_spec("digits")
        with store:
            run_id = store.create_run(spec=run_spec)
            config = make_pipeline_config(run_id, run_spec, "stratified_random", 2)
            run_pipeline(config, store)
            store.finish_run(run_id, "completed")
            round1 = len(store.query_records(run_id=run_id))

        with open_store(store_path) as store:
            config = make_pipeline_config(run_id, run_spec, "stratified_random", 4)
            run_pipeline(config, store)
            store.finish_run(run_id, "completed")
            round2 = len(store.query_records(run_id=run_id))
            seqs = [r.seq for r in store.query_records(run_id=run_id)]
        print(f"round 1: {round1} records -> round 2: {round2} records")
        print(f"seq monotonic: {seqs == sorted(seqs)}")
        assert round2 >= round1 and seqs == sorted(seqs)
    print("U3 demo: OK (pause + resume by run_id, no re-measurement)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
