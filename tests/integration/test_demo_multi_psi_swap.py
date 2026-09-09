"""D17 — multi-ψ swap: adaptation is a STATE VARIABLE, not an overwrite.

One frozen backbone (MNIST-trained MLP, θ SHA asserted bitwise invariant
across the whole lifecycle); a library of per-task solved corrections
ψ_t ∈ {MNIST, FashionMNIST, KMNIST}, each obtained by ONE closed-form
ridge solve on frozen features (instant acquisition — no episodes, no
gradients). Swapping ψ demonstrates:

1. each task reaches its own solved accuracy under its own ψ (the
   frozen-feature linear-probe ceiling);
2. off-task retention at the null level BY CONSTRUCTION — no ψ ever
   touches another task's read (swap, don't overwrite — the §24 P-B
   claim that the probe-scale 0.786 retention cost is an overwrite
   artifact);
3. task selectivity: each ψ helps its own task far more than the
   foreign tasks (the library is a keyed state variable, not a blend).

Demonstrated regime (pinned 2026-09-08): 784→(64,64)→10, 300 stage-A
episodes batch 64, 40 ridge batches per task, 512-sample fixed probe.
"""

import hashlib
from pathlib import Path

import torch
from torch import nn

from computronium import (
    CreditAssignmentConfig,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system_from_configs,
)
from computronium.core.pipeline import run_train_step
from computronium.visualization import bars_panel, figure_spec

BATCH = 64
STAGE_A_EPISODES = 300
RIDGE_BATCHES = 40
PROBE_N = 512
TASKS = ("MNIST", "FashionMNIST", "KMNIST")
REPO_ROOT = Path(__file__).resolve().parents[2]


def _dataset(name: str, train: bool) -> tuple[torch.Tensor, torch.Tensor]:
    import torchvision

    cls = getattr(torchvision.datasets, name)
    ds = cls(root=str(REPO_ROOT / "data"), train=train, download=False)
    return ds.data.float().reshape(-1, 784) / 255.0, ds.targets.long()


def _forward_acts(system, x: torch.Tensor) -> list[torch.Tensor]:
    h = x
    acts: list[torch.Tensor] = []
    for module in system.geometry._layers:
        if isinstance(module, nn.Linear):
            acts.append(h)
            h = h @ module.weight.T + module.bias
        else:
            h = module(h)
    acts.append(h)
    return acts


class _ReadoutCeiling:
    """Ridge h_last -> onehot, applied as a readout replacement (the
    frozen-feature linear-probe ceiling; the same affine class as
    post + affine(h) because the readout is itself affine in h_last)."""

    def __init__(self) -> None:
        self._gram: torch.Tensor | None = None
        self._cross: torch.Tensor | None = None

    def update(self, h: torch.Tensor, y: torch.Tensor) -> None:
        xa = torch.cat((h, torch.ones(h.shape[0], 1)), dim=-1).float()
        target = torch.nn.functional.one_hot(y, 10).float()
        g = xa.T @ xa
        c = xa.T @ target
        self._gram = g if self._gram is None else self._gram + g
        self._cross = c if self._cross is None else self._cross + c

    def solve(self) -> tuple[torch.Tensor, torch.Tensor] | None:
        if self._gram is None or self._cross is None:
            return None
        d = self._gram.shape[0]
        lam = 1e-3 * self._gram.diagonal().mean().clamp_min(1e-12)
        m_aug = torch.linalg.solve(self._gram + lam * torch.eye(d), self._cross)
        return m_aug[:-1], m_aug[-1]


def _theta_sha256(system) -> str:
    raw = b"".join(
        p.detach().cpu().contiguous().view(-1).view(torch.uint8).numpy().tobytes()
        for p in system.geometry.params.values()
    )
    return hashlib.sha256(raw).hexdigest()


def _probe(system, x: torch.Tensor, y: torch.Tensor, psi=None) -> float:
    with torch.no_grad():
        logits = _forward_acts(system, x)[-1]
        if psi is not None:
            m, b = psi
            logits = _forward_acts(system, x)[-2] @ m + b
    return (logits.argmax(-1) == y).float().mean().item()


def _train_backbone(system, data, gen) -> None:
    a_train, a_labels = data["MNIST"][0]
    for _ in range(STAGE_A_EPISODES):
        idx = torch.randint(len(a_train), (BATCH,), generator=gen)
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            a_train[idx],
            a_labels[idx],
        )


def _build_library(system, data, gen) -> dict[str, tuple[torch.Tensor, torch.Tensor]]:
    library: dict[str, tuple[torch.Tensor, torch.Tensor]] = {}
    for t in TASKS:
        x_train, y_train = data[t][0]
        ceiling = _ReadoutCeiling()
        for _ in range(RIDGE_BATCHES):
            idx = torch.randint(len(x_train), (BATCH,), generator=gen)
            with torch.no_grad():
                acts = _forward_acts(system, x_train[idx])
            ceiling.update(acts[-2], y_train[idx])
        solved = ceiling.solve()
        assert solved is not None
        library[t] = solved
    return library


def _measure(system, probes, library) -> dict[str, dict[str, float]]:
    cells: dict[str, dict[str, float]] = {}
    for t in TASKS:
        x_t, y_t = probes[t]
        foreign = [_probe(system, x_t, y_t, psi=library[o]) for o in TASKS if o != t]
        cells[t] = {
            "null_transfer": _probe(system, x_t, y_t),
            "own_psi": _probe(system, x_t, y_t, psi=library[t]),
            "foreign_psi_mean": sum(foreign) / len(foreign),
        }
    return cells


def test_demo_multi_psi_swap(emit_run_record) -> None:
    torch.manual_seed(42)
    system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.feedforward(input_dim=784, output_dim=10, hidden_dims=(64, 64)),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.euclidean(step_size=0.1),
    )
    data = {t: (_dataset(t, True), _dataset(t, False)) for t in TASKS}
    gen = torch.Generator().manual_seed(42)
    _train_backbone(system, data, gen)
    sha_before = _theta_sha256(system)

    probes = {}
    for t in TASKS:
        x_test, y_test = data[t][1]
        idx = torch.randint(len(x_test), (PROBE_N,), generator=gen)
        probes[t] = (x_test[idx], y_test[idx])

    library = _build_library(system, data, gen)
    tasks = _measure(system, probes, library)
    backbone_params = sum(p.numel() for p in system.geometry.params.values())
    psi_params_per_task = sum(m.numel() + b.numel() for m, b in library.values())

    record: dict = {
        "theta_sha256_before": sha_before,
        "theta_sha256_after": _theta_sha256(system),
        "tasks": tasks,
        "param_counts": {
            "backbone": backbone_params,
            "psi_per_task": psi_params_per_task // len(TASKS),
        },
    }

    # Guarantee 1: θ bitwise frozen across the whole lifecycle.
    assert sha_before == record["theta_sha256_after"]
    # Guarantee 2: each task is acquired under its own ψ — far above its
    # null transfer for the non-native tasks (the acquisition claim),
    # never below null for the native one (no degradation) — and the ψ
    # is selective (own ≫ foreign mean: a keyed state variable, not a
    # blend; the foreign ψ REPLACES the readout, which is why the
    # library swaps instead of overwrites).
    for t in TASKS:
        cell = record["tasks"][t]
        if cell["null_transfer"] < 0.5:
            assert cell["own_psi"] > cell["null_transfer"] + 0.2, (t, cell)
        else:
            assert cell["own_psi"] >= cell["null_transfer"] - 0.02, (t, cell)
        assert cell["own_psi"] > cell["foreign_psi_mean"] + 0.1, (t, cell)

    record["figure"] = figure_spec(
        "D17 — multi-ψ swap: one frozen θ, per-task solved ψ as a state "
        "variable (swap, don't overwrite) | "
        f"backbone {backbone_params:,} params; ψ is a per-task additive "
        f"cost ({psi_params_per_task // len(TASKS):,} params per ridge solve, not θ)",
        bars_panel(
            {
                t: {
                    "null transfer": c["null_transfer"],
                    "own ψ": c["own_psi"],
                    "foreign ψ (mean)": c["foreign_psi_mean"],
                }
                for t, c in record["tasks"].items()
            },
            chance=0.1,
            chance_label="chance (0.1)",
            ylabel="accuracy",
            ylim=(0, 1),
        ),
        figsize=[7, 4.5],
    )

    emit_run_record("D17", "multi_psi_swap", record)
