"""D20 — NTM copy under local credit (transport graph > memory machinery).

TODO16 §1.2 wraps the recorded w8_ntm_copy r6 recipe as a gallery demo:
LSTM controller + content-addressed heads on the copy task, width 16,
3000 steps, two arms — bptt control (exact gradient through the episode)
vs local3 (layer-local credit on the controller, r6 recipe with expected
writer + credit-to-controller). The transport graph stays intact in both
arms; the comparison isolates credit locality from memory machinery
(§17.9).

Measured 2026-09-25, 200-step eval cadence, seed 0
(``logs/todo34_s11_{bptt,local3}.log``). The arms are asserted on the
**tail-3 mean** of the fresh-batch curve, not on any single checkpoint:
local3 oscillates 0.59–0.87 after 1400 steps (0.854/0.594/0.833 over the
last three), so a floor on a single checkpoint is a flake waiting for a
busy machine (TODO34 §1.1). At this test's 600-step cadence the tail-3
means are bptt 0.918 (0.906/0.969/0.979) and local3 0.809
(0.844/0.750/0.833); the floors sit below both. The run record keeps the
final-iterate values (0.979 / 0.833) so the pinned figure is untouched.
The firm capability record is the 8000-step 3-seed run — local3 mean
0.944 (0.958/0.917/0.958), ``logs/breadth_ntm_copy8k_s{0,1,2}.log``.
"""

import time
from itertools import chain

import pytest
import w8_ntm_copy as ntm

from computronium.visualization._demo_api import bars_panel, figure_spec

STEPS = 3000
LR = 1e-3
SEED = 0
TAIL = 3


def _tail_mean(curve: list[float]) -> float:
    return sum(curve[-TAIL:]) / TAIL


@pytest.mark.timeout(900)
@pytest.mark.slow
def test_demo_ntm_local(emit_run_record) -> None:
    t0 = time.time()
    curves: dict[str, list[float]] = {}

    controller, heads, curves["bptt"] = ntm._run_bptt(STEPS, LR, SEED)
    bptt_params = sum(
        p.numel() for p in chain(controller.parameters(), heads.parameters())
    )
    controller, heads, curves["local3"] = ntm._run_local(
        STEPS, LR, SEED, writer="expected", label="local3", credit_controller=True
    )
    local3_params = sum(
        p.numel() for p in chain(controller.parameters(), heads.parameters())
    )
    param_counts = {"bptt": bptt_params, "local3": local3_params}
    # The record and its figure keep the final-iterate value: the tail mean is
    # the *assertion* summary, and a new summary would re-pin the manifest.
    arms = {name: curve[-1] for name, curve in curves.items()}
    for name, curve in curves.items():
        print(
            f"{name}: copy-acc {arms[name]:.3f} tail-{TAIL} mean "
            f"{_tail_mean(curve):.3f} curve {curve}"
        )
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
    assert _tail_mean(curves["local3"]) >= 0.72
    assert _tail_mean(curves["bptt"]) >= 0.88
    assert arms["local3"] < arms["bptt"]
