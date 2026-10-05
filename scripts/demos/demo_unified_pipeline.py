"""Demo: U1 end-to-end (question → RunSpec → Synthesis → pipeline → store → report).

Expected: records persisted with unique measurement keys; run finishes
completed. Same APIs as tests/acceptance/test_unified_kernel.py (U1).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _support import fresh_store, make_pipeline_config, make_run_spec, run_pipeline


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store, _ = fresh_store(Path(tmp), "u1")
        with store:
            run_spec = make_run_spec("digits")
            run_id = store.create_run(spec=run_spec)
            config = make_pipeline_config(run_id, run_spec, "synthesis", 2)
            records = run_pipeline(config, store)
            stored = store.query_records(run_id=run_id)
            store.finish_run(run_id, "completed")
        print(f"records produced: {len(records)}")
        print(f"records persisted: {len(stored)}")
        print(f"unique measurement keys: {len({r.measurement_key for r in records})}")
        assert stored and len(stored) == len(records)
    print("U1 demo: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
