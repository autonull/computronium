"""The CLI mutes its own advisory hints, not every UserWarning.

`comp` used to install a blanket ``ignore::UserWarning`` filter, which hid any
warning raised by any dependency for the rest of the process. The filters are
now message-targeted; this test holds that boundary.
"""

from __future__ import annotations

import warnings

import pytest


@pytest.fixture
def cli_filters() -> list[warnings.WarningMessage]:
    import computronium.cli.__main__ as cli  # ruff: ignore[unused-import]  (import installs filters)

    messages = (
        "PC-ALM beta mismatch: dynamics.beta=0.1 != credit.beta=0.2",
        "Diffusion dynamics (Langevin) with substrate noise_level=0.0 has no noise",
        "update_type=euclidean uses per-element-displacement step semantics; "
        "step_size=0.1 is in the gradient-relative lr range",
        "an unrelated warning from a dependency",
    )
    with warnings.catch_warnings(record=True) as caught:
        for message in messages:
            warnings.warn(message, UserWarning)
    return caught


def test_advisory_hints_are_quiet(cli_filters: list[warnings.WarningMessage]) -> None:
    assert [str(warning.message) for warning in cli_filters] == [
        "an unrelated warning from a dependency"
    ]


def test_no_blanket_user_warning_filter() -> None:
    import computronium.cli.__main__ as cli  # ruff: ignore[unused-import]

    for action, message, category, module, _lineno in warnings.filters:
        if action == "ignore" and category is UserWarning:
            assert message is not None and module is None, (
                "a blanket UserWarning filter hides unrelated warnings"
            )
