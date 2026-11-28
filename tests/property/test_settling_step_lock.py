"""W64: the settling step's decisions, locked on what each one chooses.

The step path in ``core/local_learning/settling.py`` was uncovered: the
momentum update, the adaptive step size, the energy convergence test and the
divergence refusal. Each is a decision (D6):

* **The momentum buffer is the running gradient**, and the state moves by
  ``lr`` times it; an unused state is left alone.
* **Adaptive settling rejects an increase**: it restores the backup and
  decays the step, and it does not grow the step right after a restore.
* **A convergence tolerance is absolute or relative**: the counter resets
  on a rise and stops at patience; no tolerance never stops.
* **A NaN or infinite energy is refused by name**, not propagated.
"""

from __future__ import annotations

import pytest
import torch

from computronium.core.local_learning.settling import (
    _check_energy_convergence,
    _energy_gradient_descent_step,
    _handle_adaptive_lr,
    energy_gradient_descent,
)


def _quadratic(states: list[torch.Tensor]) -> torch.Tensor:
    residuals = torch.stack([(state - 2.0).pow(2).sum() for state in states])
    return 0.5 * residuals.sum()


def test_the_step_applies_momentum_to_the_gradient() -> None:
    state = torch.zeros(1, requires_grad=True)
    energy, grads = _energy_gradient_descent_step(
        [state],
        _quadratic,
        [torch.zeros(1)],
        lr=0.1,
        momentum=0.5,
    )

    assert energy == pytest.approx(2.0)
    assert grads[0] is not None
    assert torch.allclose(state.detach(), torch.tensor([0.2]))


def test_the_step_leaves_an_state_with_no_gradient_alone() -> None:
    untouched = torch.zeros(1, requires_grad=True)
    moved = torch.zeros(1, requires_grad=True)

    _energy_gradient_descent_step(
        [untouched, moved],
        lambda states: (states[1] - 3.0).pow(2).sum(),
        [torch.zeros(1), torch.zeros(1)],
        lr=0.1,
        momentum=0.0,
    )

    assert torch.equal(untouched.detach(), torch.zeros(1))
    assert moved.detach().item() == pytest.approx(0.6)


def test_the_step_refuses_a_diverged_energy_by_name() -> None:
    state = torch.zeros(1, requires_grad=True)

    with pytest.raises(RuntimeError, match="Energy diverged"):
        _energy_gradient_descent_step(
            [state],
            lambda _states: torch.tensor(float("nan")),
            [torch.zeros(1)],
            lr=0.1,
            momentum=0.0,
        )


def test_adaptive_settling_restores_and_decays_on_a_rise() -> None:
    current = torch.tensor([5.0])
    backup = torch.tensor([2.0])
    states = [current]

    new_lr, restored, new_backup = _handle_adaptive_lr(
        states,
        [backup],
        current_energy=10.0,
        prev_energy=1.0,
        current_lr=0.4,
        just_restored=False,
        step_size_growth=1.5,
        step_size_decay=0.5,
        lr=0.4,
    )

    assert new_lr == pytest.approx(0.2)
    assert restored is True
    assert torch.equal(states[0], torch.tensor([2.0]))
    assert new_backup is not None


def test_adaptive_settling_does_not_grow_right_after_a_restore() -> None:
    states = [torch.tensor([1.0])]
    backups = [torch.tensor([1.0])]

    new_lr, restored, _ = _handle_adaptive_lr(
        states,
        backups,
        current_energy=1.0,
        prev_energy=2.0,
        current_lr=0.2,
        just_restored=True,
        step_size_growth=1.5,
        step_size_decay=0.5,
        lr=0.4,
    )

    assert new_lr == pytest.approx(0.2)
    assert restored is False


def test_adaptive_settling_grows_on_an_accepted_step_up_to_ten_lr() -> None:
    states = [torch.tensor([1.0])]
    backups = [torch.tensor([1.0])]

    new_lr, restored, _ = _handle_adaptive_lr(
        states,
        backups,
        current_energy=1.0,
        prev_energy=2.0,
        current_lr=3.0,
        just_restored=False,
        step_size_growth=2.0,
        step_size_decay=0.5,
        lr=0.4,
    )

    assert new_lr == pytest.approx(4.0)  # min(6.0, 10 * 0.4)
    assert restored is False


def test_a_missing_phase_keeps_the_learning_rate_and_backup() -> None:
    new_lr, restored, backup = _handle_adaptive_lr(
        [torch.zeros(1)],
        None,
        current_energy=1.0,
        prev_energy=None,
        current_lr=0.3,
        just_restored=False,
        step_size_growth=1.1,
        step_size_decay=0.5,
        lr=0.3,
    )

    assert (new_lr, restored, backup) == (0.3, False, None)


def test_no_tolerance_never_stops() -> None:
    should_stop, counter, previous = _check_energy_convergence(
        1.0, 1.0, 7, tol=None, patience=2
    )

    assert (should_stop, counter, previous) == (False, 7, 1.0)


def test_the_relative_tolerance_counts_a_small_change() -> None:
    should_stop, counter, _ = _check_energy_convergence(
        5.0, 10.0, 0, tol=1.0, patience=3
    )

    assert should_stop is False
    assert counter == 1  # 5 < 1 * max(1, 10)

    should_stop, counter, _ = _check_energy_convergence(
        5.0, 10.0, 0, tol=0.1, patience=3
    )
    assert counter == 0  # 5 >= 0.1 * 10


def test_the_counter_stops_at_patience_and_resets_on_a_rise() -> None:
    should_stop, counter, _ = _check_energy_convergence(
        1.0, 1.0, 1, tol=1e-6, patience=2
    )
    assert should_stop is True and counter == 2

    should_stop, counter, _ = _check_energy_convergence(
        2.0, 1.0, 1, tol=1e-6, patience=2
    )
    assert should_stop is False and counter == 0


def test_a_constant_energy_stops_at_patience() -> None:
    calls = 0

    def constant(states: list[torch.Tensor]) -> torch.Tensor:
        nonlocal calls
        calls += 1
        return (states[0] * 0.0).sum() + 5.0

    state = torch.zeros(1, requires_grad=True)
    energy_gradient_descent([state], constant, steps=100, tol=1e-6, patience=2)

    assert calls == 3  # first call has no previous energy, then two hits


def test_adaptive_descent_recovers_from_an_overshooting_step() -> None:
    state = torch.zeros(1, requires_grad=True)

    final = energy_gradient_descent(
        [state],
        _quadratic,
        steps=50,
        lr=10.0,
        momentum=0.0,
        adaptive=True,
    )[0]

    assert abs(final.item() - 2.0) < 2.0
    assert not final.requires_grad
