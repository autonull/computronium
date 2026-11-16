"""The parity ladder runner actually runs, and its batch is a parameter.

``run_parity`` is the cell runner TODO93's memory ladder reuses, so it has to
be runnable: it called ``backprop_baseline(batch_size=...)`` for a parameter
that function did not have, and every campaign raised ``NameError`` before a
single cell was trained. The batch is also a *claim* parameter (the binding gate
is ``B·W·L`` against params + optimizer), so a ladder that varies it must do so
here rather than build a second depth loop.

The task is ``iris`` at one depth: the assertion is that the runner returns a
baseline and the named family, not that a local rule wins.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from computronium.validation.backprop_parity import run_parity

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("batch_size", [32, 64])
def test_the_ladder_runner_trains_a_baseline_and_a_family_cell(
    batch_size: int, tmp_path: Path
) -> None:
    report = run_parity(
        task="iris",
        depths=(1,),
        epochs=1,
        seeds=1,
        device="cpu",
        families=("pepita",),
        output_dir=tmp_path,
        width_ladder=(),
        batch_size=batch_size,
    )

    models = cast("dict[str, dict[str, object]]", report["models"])
    assert "backprop_mlp@1" in models
    assert "pepita@1" in models
    assert models["backprop_mlp@1"]["epochs"] == 1
    assert (tmp_path / "results.json").exists()
