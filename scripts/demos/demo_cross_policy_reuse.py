"""Demo: U5 cross-policy evidence reuse — one store, no migration.

Expected: Random -> TPE -> Evolution phases share one store; identical
legality/claims machinery; same record schema throughout.
Same APIs as tests/acceptance/test_unified_kernel.py (U5).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _support import fresh_store, make_pipeline_config, make_run_spec, run_pipeline


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store, _ = fresh_store(Path(tmp), "u5")
        run_spec = make_run_spec("digits")
        phases = ("uniform_random", "model_based_tpe", "evolution")
        all_records = []
        with store:
            for phase in phases:
                run_id = store.create_run(spec=run_spec)
                config = make_pipeline_config(run_id, run_spec, phase, 2)
                records = run_pipeline(config, store)
                assert records, f"{phase} produced no records"
                all_records.extend(records)
                store.finish_run(run_id, "completed")
        print(f"phases: {phases}")
        print(f"total records in one store: {len(all_records)}")
        assert all(r.substrate and r.geometry and r.dynamics for r in all_records)
        assert all(r.schedule.fidelity == "L0" for r in all_records)
    print("U5 demo: OK (no migration, same identity/legality/claims)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
