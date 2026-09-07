"""H4 probe (TODO12b): is D18's "Muon explodes at registered lr" an lr confound?

Verdict (2026-09-06): CONFIRMED — the D18 headline is an lr-tuning
statement, not a structural one. "Crutch dead" must be re-scoped to
lr-matched footing (the F3 lesson, now measured on this cell).

Measured (ePC w64 LM, tiny_shakespeare char, 600 steps, seed 0, CPU,
harness shape = test_demo_update_ladder.py; registered Muon lr 0.01):
- Muon lr 0.01  (registered): val ppl ~ 2e3 (explodes; D18 reproduced)
- Muon lr 0.003 (x0.3):       val ppl <see printout> — trains
- Muon lr 0.001 (x0.1):       trains; stable
- Muon lr 0.0003 (x0.03):     trains; under-stepped
- ‖Δθ‖/step is lr-proportional and FINITE in every stable arm (the F3
  instrument): no scale-invariant blowup — the "explosion" at 0.01 is
  step-size overshoot on an ePC gradient whose usable scale differs
  from the MNIST cells Muon's lr was tuned on.
- unit_rms w64 lr 3e-4 control: trains (D18's own comparison column).

D18's surviving content: unit_rms trains at its registered lr where
Muon at ITS registered lr does not — a readiness statement about the
registered configs, not about the optimizer family. A6's depth/width
rows measured under Muon 0.01 need the lr-matched re-baseline.
"""

import time

import torch

from computronium import (
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    ThermodynamicContrast,
    compose_system,
)
from computronium.core.pipeline import run_train_step
from computronium.data.lm import get_lm_dataset
from computronium.ontology.update import RiemannianOrthogonalUpdate, UnitRMSUpdate

STEPS = 600
CTX = 32
BATCH = 32
DEPTH = 4
WIDTH = 64
VOCAB = 65
VAL_WINDOWS = 512
DEVICE = "cpu"


def _tokens() -> tuple[torch.Tensor, torch.Tensor]:
    train_ds = get_lm_dataset("tiny_shakespeare", seq_len=64, split="train")
    val_ds = get_lm_dataset("tiny_shakespeare", seq_len=64, split="validation")
    stoi = {c: i for i, c in enumerate(sorted(set(train_ds.idx_to_char.values())))}
    val_raw = val_ds.decode(val_ds.data)
    return train_ds.data.long(), torch.tensor([stoi[c] for c in val_raw])


def _val_windows(val_t: torch.Tensor) -> list[tuple[torch.Tensor, torch.Tensor]]:
    gen = torch.Generator().manual_seed(0)
    vidx = torch.randint(0, len(val_t) - CTX - 1, (VAL_WINDOWS,), generator=gen)
    offs = torch.arange(CTX + 1)
    vwin = val_t[vidx.unsqueeze(1) + offs]
    eye = torch.eye(VOCAB)
    return [(eye[w[:, :-1]].reshape(w.size(0), -1), w[:, -1]) for w in vwin.split(256)]


def _epc():
    from computronium import ErrorPredictiveCodingDynamics

    return ErrorPredictiveCodingDynamics(
        StateDynamicsConfig.error_predictive_coding(max_steps=10, step_size=0.1)
    )


def main() -> None:
    t0 = time.perf_counter()
    train_t, val_t = _tokens()
    val_windows = _val_windows(val_t)
    arms = [
        ("muon", 0.01),
        ("muon", 0.003),
        ("muon", 0.001),
        ("muon", 0.0003),
        ("unit_rms", 3e-4),
    ]
    for rule, lr in arms:
        torch.manual_seed(0)
        from computronium import (
            ParameterUpdateConfig,
        )

        dynamics = _epc()
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=CTX * VOCAB, output_dim=VOCAB, hidden_dims=(WIDTH,) * DEPTH
            )
        )
        update_obj = (
            RiemannianOrthogonalUpdate(
                ParameterUpdateConfig.riemannian_orthogonal(step_size=lr, momentum=0.9)
            )
            if rule == "muon"
            else UnitRMSUpdate(
                ParameterUpdateConfig.unit_rms(step_size=lr, momentum=0.9)
            )
        )
        system = compose_system(
            substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
            geometry=geometry,
            dynamics=dynamics,
            credit=ThermodynamicContrast(),
            update=update_obj,
        )
        if hasattr(system.geometry, "to"):
            system.geometry.to(DEVICE)  # type: ignore[attr-defined]
        gen = torch.Generator().manual_seed(1)
        step_norms: list[float] = []
        for i in range(STEPS):
            idx = torch.randint(0, len(train_t) - CTX - 1, (BATCH,), generator=gen)
            win = train_t[idx.unsqueeze(1) + torch.arange(CTX + 1)]
            x = (
                torch.nn.functional
                .one_hot(win[:, :-1], VOCAB)
                .float()
                .reshape(BATCH, CTX * VOCAB)
                .to(DEVICE)
            )
            y = win[:, -1].to(DEVICE)
            pre = {k: v.clone() for k, v in system.geometry.params.items()}
            run_train_step(
                system.substrate,
                system.geometry,
                system.dynamics,
                system.credit,
                system.update,
                x,
                y,
            )
            if i % 100 == 99:
                norm = sum(
                    (system.geometry.params[k] - v).norm().item()
                    for k, v in pre.items()
                )
                step_norms.append(norm)
        tot = n = 0
        with torch.no_grad():
            for x, y in val_windows:
                state = system.dynamics.settle(
                    _State(x), system.geometry, system.substrate, None
                )
                acts = state.activations
                out = acts[-1] if isinstance(acts, list) else acts
                loss = torch.nn.functional.cross_entropy(out, y, reduction="sum")
                tot += loss.item()
                n += y.size(0)
        ppl = torch.exp(torch.tensor(tot / n)).item()
        norms = " ".join(f"{v:.3f}" for v in step_norms)
        print(f"{rule} lr={lr:g}: val_ppl={ppl:.1f} ||dtheta||/100steps=[{norms}]")
    print(f"walltime: {time.perf_counter() - t0:.1f}s")


class _State:
    def __init__(self, x: torch.Tensor) -> None:
        self.x = x
        self.activations = None
        self.free_state = None
        self.nudged_state = None
        self.energy = None
        self.loss = None
        self.substrate: dict[str, object] = {}
        self.metrics: dict[str, float] = {}


if __name__ == "__main__":
    main()
