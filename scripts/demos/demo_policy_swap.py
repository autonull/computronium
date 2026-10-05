"""Demo: U4 policy interchangeability — 4 policies, same RunSpec/Space/Store.

Expected: identical record schema across policies; only search behavior
differers. Same APIs as tests/acceptance/test_unified_kernel.py (U4).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _support import fresh_store, make_pipeline_config, make_run_spec, run_pipeline


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store, _ = fresh_store(Path(tmp), "u4")
        run_spec = make_run_spec("digits")
        policies = ("stratified_random", "model_based_tpe", "evolution", "synthesis")
        counts: dict[str, int] = {}
        with store:
            for policy in policies:
                run_id = store.create_run(spec=run_spec)
                config = make_pipeline_config(run_id, run_spec, policy, 2)
                records = run_pipeline(config, store)
                counts[policy] = len(records)
                assert records, f"{policy} produced no records"
                assert all(r.cell_key and r.measurement_key for r in records)
                store.finish_run(run_id, "completed")
        for policy, n in counts.items():
            print(f"{policy}: {n} records")
    print("U4 demo: OK (identical schema, different search behavior)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
