"""Lock: the kernel attach guard probes once per cell and detaches on mismatch.

The guard answers a per-cell question — does this rung reproduce the composed
system's forward? — but it used to pay one forward plus one kernel equilibrium
per seed, because the decision was not cached (TODO107 D6). It also must keep
the reference rung when the rung disagrees; the eqprop kernel is reference-only
on a composed relu cell, and a guard that attaches anyway trains a different
network than the one it reports (TODO107 D5).
"""

from __future__ import annotations

import torch

from computronium.experiment.kernel import evaluate


class _Coordinate:
    def __init__(self, key: str) -> None:
        self._key = key

    def cell_key(self) -> str:
        return self._key


class _Task:
    name = "digits"
    input_dim = (64,)
    output_dim = 10


class _AlgorithmSpec:
    id = "algorithm.eqprop"
    status = "kernel_verified"


class _System:
    def __init__(self) -> None:
        self._kernel_backend: object | None = None
        self.detached = 0

    def detach_kernel_backend(self) -> None:
        self.detached += 1
        self._kernel_backend = None


def test_one_parity_probe_per_unique_cell(monkeypatch) -> None:
    """Two seeds of one cell share the attach decision; a new cell probes."""
    calls: list[int] = []

    def fake_matches(*_args, **_kwargs) -> bool:
        calls.append(1)
        return True

    monkeypatch.setattr(evaluate, "_kernel_matches_reference", fake_matches)
    evaluate._PARITY_CACHE.clear()
    system, backend, task, alg_spec = _System(), object(), _Task(), _AlgorithmSpec()
    probe = torch.zeros(1, 64)

    first = evaluate._kernel_matches_cell(
        _Coordinate("cell-a"), {}, task, system, backend, alg_spec, probe
    )
    second = evaluate._kernel_matches_cell(
        _Coordinate("cell-a"), {}, task, system, backend, alg_spec, probe
    )
    third = evaluate._kernel_matches_cell(
        _Coordinate("cell-b"), {}, task, system, backend, alg_spec, probe
    )

    assert first and second and third
    assert len(calls) == 2, f"probed {len(calls)} times for two cells"


def test_a_mismatched_rung_detaches_to_the_reference(monkeypatch) -> None:
    """A rung that does not reproduce the cell's forward must not stay attached."""
    import computronium.acceleration.dispatch as dispatch_module
    import computronium.acceleration.registry as registry_module

    alg_spec = _AlgorithmSpec()

    def fake_finish(system: _System, _spec: object, _rung: str) -> None:
        system._kernel_backend = object()

    monkeypatch.setattr(
        registry_module, "find_algorithm_for_coordinate", lambda _coordinate: alg_spec
    )
    monkeypatch.setattr(dispatch_module, "finish_with_backend", fake_finish)
    monkeypatch.setattr(evaluate, "_parity_probe", lambda *_args: torch.zeros(1, 64))

    mismatch = _System()
    monkeypatch.setattr(evaluate, "_kernel_matches_reference", lambda *_args: False)
    evaluate._attach_algorithm_kernel_backend(
        mismatch, _Coordinate("relu-cell"), _Task(), "cpu", {}
    )
    assert mismatch.detached == 1
    assert mismatch._kernel_backend is None

    match = _System()
    monkeypatch.setattr(evaluate, "_kernel_matches_reference", lambda *_args: True)
    evaluate._attach_algorithm_kernel_backend(
        match, _Coordinate("tanh-cell"), _Task(), "cpu", {}
    )
    assert match.detached == 0
    assert match._kernel_backend is not None
