"""D20 — NTM copy under local credit (transport graph > memory machinery).

TODO16 §1.2 wraps the recorded w8_ntm_copy r6 recipe as a gallery demo:
LSTM controller + content-addressed heads on the copy task, width 16,
3000 steps, two arms — bptt control (exact gradient through the episode)
vs local3 (layer-local credit on the controller, r6 recipe with expected
writer + credit-to-controller). The transport graph stays intact in both
arms; the comparison isolates credit locality from memory machinery
(§17.9).

Measured (w8_ntm_promo_r6 logs, 2026-09-08): bptt 0.979, local3
oscillates 0.79-0.87 at 3000 steps (assert floor 0.80); the firm
capability record is the 8000-step 3-seed run — local3 mean 0.944
(0.958/0.917/0.958), `logs/breadth_ntm_copy8k_s{0,1,2}.log`.
"""

import sys
import time
from itertools import chain
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "probes"))

import w8_ntm_copy as ntm

from computronium.visualization._demo_api import bars_panel, figure_spec

STEPS = 3000
LR = 1e-3
SEED = 0


def _acc(controller, heads) -> float:
    return float(ntm._greedy_copy_acc(controller, heads, ntm._eval_batch()))


@pytest.mark.timeout(900)
def test_demo_ntm_local(emit_run_record) -> None:
    t0 = time.time()
    arms: dict[str, float] = {}

    controller, heads, _ = ntm._run_bptt(STEPS, LR, SEED)
    arms["bptt"] = _acc(controller, heads)
    bptt_params = sum(
        p.numel() for p in chain(controller.parameters(), heads.parameters())
    )

    controller, heads, _ = ntm._run_local(
        STEPS, LR, SEED, writer="expected", label="local3", credit_controller=True
    )
    arms["local3"] = _acc(controller, heads)
    local3_params = sum(
        p.numel() for p in chain(controller.parameters(), heads.parameters())
    )
    param_counts = {"bptt": bptt_params, "local3": local3_params}
    for name, acc in arms.items():
        print(f"{name}: copy-acc {acc:.3f}")
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")

    emit_run_record(
        "D20",
        "ntm_local",
        {
            "steps": STEPS,
            "lr": LR,
            "seed": SEED,
            "width": ntm.MEM_WIDTH,
            "arms": arms,
            "param_counts": param_counts,
            "figure": figure_spec(
                "D20 — NTM copy: local credit vs bptt control (r6 recipe; "
                f"matched params: {bptt_params:,} / {local3_params:,})",
                bars_panel(
                    {"copy task / r6 recipe / 3000 steps": arms},
                    xlabel="",
                    ylabel="copy-acc (fresh)",
                    chance=0.5,
                ),
            ),
        },
    )
    assert arms["local3"] >= 0.80
    assert arms["bptt"] >= 0.97
