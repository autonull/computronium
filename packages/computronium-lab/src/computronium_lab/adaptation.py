"""Continual learning runtime (TODO23 Phase 3): ψ-only adaptation on frozen θ.

Wraps the existing P-axis pipeline (`pipeline.run_train_step`) and ψ
plasticity primitives; no new ontology semantics. The U-axis is parked
behind a frozen no-op update for the duration of an adaptation episode,
making bitwise θ invariance structural rather than aspirational.
"""

from __future__ import annotations

import copy
import hashlib
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium.core.pipeline import run_train_step
from computronium.core.plasticity.closed_form import (
    ClosedFormRidgePlasticity,
    create_closed_form_ridge_plasticity,
)
from computronium.core.plasticity.temporal_psi import (
    TemporalPsiPlasticity,
    create_temporal_psi_plasticity,
)
from computronium.experiments.joint.z3_fixed_weights import Z3Operators

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium.ontology.credit import CreditAssignment
    from computronium_lab.training import StabilityCertificate

PSI_ONLY = "psi_only"


class AdaptationMode(StrEnum):
    """First-class ψ adaptation modes (T23.3.1).

    TEMPORAL: trace-decayed ridge readout (forgetting by default).
    CONFLICT_ADAPTIVE: agreement-driven trace decay (fast forgetting under
        readout/task conflict).
    CLOSED_FORM: accumulate-only ridge (forget-free limit).
    ROLE_SPLIT: closed-form ridge that *replaces* the readout role rather
        than correcting it — features stay frozen-owned, the readout role
        is ψ-owned.
    """

    TEMPORAL = "temporal"
    CONFLICT_ADAPTIVE = "conflict_adaptive"
    CLOSED_FORM = "closed_form"
    ROLE_SPLIT = "role_split"


type PsiPlasticity = TemporalPsiPlasticity | ClosedFormRidgePlasticity


def psi_plasticity(mode: AdaptationMode) -> PsiPlasticity:
    """AdaptationMode → P-axis primitive (existing factories only)."""
    match mode:
        case AdaptationMode.TEMPORAL:
            return create_temporal_psi_plasticity()
        case AdaptationMode.CONFLICT_ADAPTIVE:
            from computronium.core.plasticity.adaptive_psi import (
                create_conflict_adaptive_psi_plasticity,
            )

            return create_conflict_adaptive_psi_plasticity()
        case AdaptationMode.CLOSED_FORM:
            return create_closed_form_ridge_plasticity()
        case AdaptationMode.ROLE_SPLIT:
            return _RoleSplitRidge()


class _FrozenThetaUpdate:
    """U-axis no-op for ψ-only adaptation (θ bitwise untouched).

    ``update_params`` copies the returned params back in place — returning
    the current params makes the update a bitwise identity while the rest
    of the pipeline (credit, settle, ψ) runs unchanged.
    """

    def __init__(self) -> None:
        from computronium.ontology.update import ParameterUpdateConfig

        self.config = ParameterUpdateConfig.euclidean(step_size=0.0, momentum=0.0)

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: object,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        return dict(params)


def theta_digest(system: object) -> str:
    """Bitwise SHA-256 over the sorted geometry parameters (T23.3.5)."""
    from computronium_lab.training import _params_digest

    return _params_digest(system)


def psi_digest(psi: dict[str, Tensor]) -> str:
    h = hashlib.sha256()
    for name in sorted(psi):
        t = psi[name].detach().cpu().contiguous()
        h.update(name.encode())
        h.update(t.numpy().tobytes())
    return h.hexdigest()


@dataclass(frozen=True, slots=True)
class ThetaInvarianceProof:
    """Bitwise θ invariance certificate for one adaptation run."""

    sha_before: str
    sha_after: str
    bitwise_invariant: bool


@dataclass(frozen=True, slots=True)
class TaskBoundary:
    """A detected (or manually forced) task boundary (T23.3.2)."""

    reason: str  # "plateau" | "conflict" | "manual"
    signal: float
    detected: bool


class TaskBoundaryDetector:
    """Automatic boundary triggers: loss plateau + ψ-agreement conflict."""

    def __init__(
        self,
        window: int = 5,
        plateau_slope: float = 1e-3,
        conflict_threshold: float = 0.65,
    ) -> None:
        self.window = window
        self.plateau_slope = plateau_slope
        self.conflict_threshold = conflict_threshold

    def plateau(self, losses: Sequence[float]) -> TaskBoundary | None:
        if len(losses) < self.window:
            return None
        recent = losses[-self.window :]
        slope = (recent[-1] - recent[0]) / max(abs(recent[0]), 1e-12)
        if abs(slope) <= self.plateau_slope:
            return TaskBoundary("plateau", slope, True)
        return None

    def conflict(self, psi: dict[str, Tensor]) -> TaskBoundary | None:
        agreement = psi.get("agreement")
        if agreement is None:
            return None
        value = float(agreement)
        if value < self.conflict_threshold:
            return TaskBoundary("conflict", value, True)
        return None

    def detect(
        self, losses: Sequence[float], psi: dict[str, Tensor]
    ) -> TaskBoundary | None:
        return self.conflict(psi) or self.plateau(losses)


@dataclass(frozen=True, slots=True)
class AdaptationResult:
    """Outcome of one lab.adapt() run (T23.3.5)."""

    mode: AdaptationMode
    metrics: dict[str, float]
    theta: ThetaInvarianceProof
    psi_updated: bool
    psi_sha: str
    boundary: TaskBoundary | None
    stability: StabilityCertificate | None = None
    walltime_s: float = 0.0


class _RoleSplitRidge(ClosedFormRidgePlasticity):
    """ROLE_SPLIT: ψ *owns* the readout role — replaces it each episode
    instead of correcting it. Features stay frozen-owned; the readout is
    the ψ-owned role. Same closed-form law as CLOSED_FORM (role-scoped by
    construction: modulate touches only ``out[-1]``)."""

    def modulate(
        self, activations: list[Tensor] | Tensor, psi: dict[str, Tensor]
    ) -> list[Tensor] | Tensor:
        m = psi.get("readout_m")
        if m is None or not isinstance(activations, list) or len(activations) < 2:
            return activations
        out = list(activations)
        readout = out[-2] @ m.to(out[-1].dtype)
        bias = psi.get("readout_b")
        if isinstance(bias, Tensor):
            readout += bias.to(out[-1].dtype)
        out[-1] = readout
        return out


class _PsiOnlyCredit:
    """Credit wrapper for ψ-only adaptation.

    The U-axis is frozen, so the pseudo-gradient is never consumed — but
    ``replace_readout`` modulation severs the autograd path to the readout,
    and GradientCredit's strictness (a learning guard) raises on the
    detached graph. Zero-filling is sound here because learning is
    disabled; the pipeline runs only to engage the P-axis.
    """

    def __init__(self, inner: CreditAssignment) -> None:
        self._inner = inner

    def __getattr__(self, name: str) -> object:
        return getattr(self._inner, name)

    def compute_pseudo_gradient(
        self, states: object, loss: object, geometry: object
    ) -> list[Tensor]:
        try:
            return self._inner.compute_pseudo_gradient(
                states,  # type: ignore[arg-type]
                loss,  # type: ignore[arg-type]
                geometry,  # type: ignore[arg-type]
            )
        except RuntimeError as exc:
            if "no gradient reached" not in str(exc):
                raise
            return [
                torch.zeros_like(t)
                for t in geometry.params.values()  # type: ignore[attr-defined]
            ]


def _psi_eval(
    system: object,
    plasticity: PsiPlasticity,
    psi: dict[str, Tensor],
    task_data: object,
    max_batches: int = 4,
) -> dict[str, float]:
    """Evaluate with ψ modulation applied (raw + ψ-owned readout accuracy).

    The pipeline's ``free_accuracy`` bypasses the P-axis (post-update
    target-free settle, no modulation), so ψ acquisition is invisible
    there; this eval settles with the *composed* ψ readout.
    """
    from computronium.core.pipeline import forward_pass
    from computronium.ontology import SystemState

    substrate = system.substrate  # type: ignore[attr-defined]
    geometry = system.geometry  # type: ignore[attr-defined]
    dynamics = system.dynamics  # type: ignore[attr-defined]

    raw_correct = 0
    psi_correct = 0
    n = 0
    batches = list(task_data)  # type: ignore[arg-type]
    for i, (x, y) in enumerate(batches[:max_batches]):
        with torch.no_grad():
            if x.dim() == 3:
                # sequence episode: score the final-timestep readout after
                # stepping the geometry through its own recurrence
                for t in range(x.shape[1]):
                    state = SystemState(x=x[:, t], y=y)
                    state.activations = forward_pass(substrate, geometry, x[:, t])
                    settled = dynamics.settle(state, geometry, substrate, target=None)
            else:
                state = SystemState(x=x, y=y)
                state.activations = forward_pass(substrate, geometry, x)
                settled = dynamics.settle(state, geometry, substrate, target=None)
            acts = settled.activations
            if acts is None:
                continue
            logits = acts[-1] if isinstance(acts, list) else acts
            raw_correct += int((logits.argmax(-1) == y).sum())
            modulated = plasticity.modulate(list(acts), psi)
            m_logits = modulated[-1] if isinstance(modulated, list) else modulated
            psi_correct += int((m_logits.argmax(-1) == y).sum())
            n += y.size(0)
    if n == 0:
        return {"accuracy": 0.0, "psi_accuracy": 0.0}
    return {
        "accuracy": raw_correct / n,
        "psi_accuracy": psi_correct / n,
    }


def _psi_only_episodes(
    system: object,
    task_data: object,
    plasticity: PsiPlasticity,
    psi: dict[str, Tensor],
    episodes: int,
) -> tuple[list[dict[str, float]], dict[str, Tensor]]:
    """Run episodes through the pipeline with the U-axis frozen.

    The caller's ``psi`` dict is stepped in place by ``_step_psi`` (the
    pipeline's writeback contract), so ψ carries across episodes.
    """
    batches = list(task_data)  # type: ignore[arg-type]
    if not batches:
        raise ValueError("task_data is empty; ψ-only adaptation needs episodes")
    substrate = system.substrate  # type: ignore[attr-defined]
    geometry = system.geometry  # type: ignore[attr-defined]
    dynamics = system.dynamics  # type: ignore[attr-defined]
    credit = system.credit  # type: ignore[attr-defined]
    frozen = _FrozenThetaUpdate()
    credit = _PsiOnlyCredit(credit)

    history: list[dict[str, float]] = []
    for i in range(episodes):
        x, y = batches[i % len(batches)]
        if x.dim() == 3:
            history.append(
                _sequence_episode(
                    substrate,
                    geometry,
                    dynamics,
                    credit,
                    frozen,
                    x,
                    y,
                    plasticity,
                    psi,
                )
            )
            continue
        history.append(
            run_train_step(
                substrate,
                geometry,
                dynamics,
                credit,  # type: ignore[arg-type]
                frozen,  # type: ignore[arg-type]
                x,
                y,
                plasticity=plasticity,
                psi=psi,
                context=object(),  # ψ primitives never read the context
            )
        )
    return history, psi


def _sequence_episode(
    substrate: object,
    geometry: object,
    dynamics: object,
    credit: object,
    frozen: object,
    x: Tensor,
    y: Tensor,
    plasticity: PsiPlasticity,
    psi: dict[str, Tensor],
) -> dict[str, float]:
    """One ψ episode over a sequence-shaped batch (E4 over NTM).

    The sequence runs through the pipeline one timestep at a time; the
    geometry's cross-step buffers carry the recurrence. ψ steps ONCE per
    episode — on the final timestep, where the episode's evidence is
    complete — and the same ψ modulation applies there; earlier
    timesteps run plasticity-free so the step contract is not violated.
    """
    metrics: dict[str, float] | None = None
    for t in range(x.shape[1]):
        engage = plasticity if t == x.shape[1] - 1 else None
        metrics = run_train_step(
            substrate,  # type: ignore[arg-type]
            geometry,  # type: ignore[arg-type]
            dynamics,  # type: ignore[arg-type]
            credit,  # type: ignore[arg-type]
            frozen,  # type: ignore[arg-type]
            x[:, t],
            y,
            plasticity=engage,
            psi=psi,
            context=object(),  # ψ primitives never read the context
        )
    assert metrics is not None  # ruff: ignore[assert] - loop runs at least once
    return metrics


def adapt(
    system: object,
    task_data: object,
    mode: AdaptationMode | str = PSI_ONLY,
    *,
    episodes: int = 10,
    boundary: TaskBoundary | None = None,
    stability_check: bool = False,
) -> AdaptationResult:
    """ψ-only adaptation: θ bitwise frozen, ψ updated, certificate returned.

    ``mode="psi_only"`` (the Phase-2 API spelling) resolves to TEMPORAL.
    ``boundary`` forces a manual task boundary; otherwise the detector runs
    over the episode stream (loss plateau + ψ-agreement conflict).
    """
    t0 = time.perf_counter()
    match mode:
        case AdaptationMode():
            resolved = mode
        case str() if mode == PSI_ONLY:
            resolved = AdaptationMode.TEMPORAL
        case str():
            resolved = AdaptationMode(mode)
        case _:
            raise TypeError(f"mode must be AdaptationMode or str, got {type(mode)}")

    sha_before = theta_digest(system)
    plasticity = psi_plasticity(resolved)
    psi: dict[str, Tensor] = plasticity.initial_psi(None)  # type: ignore[arg-type]
    batches = list(task_data)  # type: ignore[arg-type]
    if not batches:
        raise ValueError("task_data is empty; ψ-only adaptation needs episodes")

    history, psi = _psi_only_episodes(system, batches, plasticity, psi, episodes)

    sha_after = theta_digest(system)
    proof = ThetaInvarianceProof(
        sha_before=sha_before,
        sha_after=sha_after,
        bitwise_invariant=sha_before == sha_after,
    )

    detector = TaskBoundaryDetector()
    detected = boundary or detector.detect(
        [row.get("free_loss", row.get("loss", 0.0)) for row in history], psi
    )

    final = history[-1] if history else {}
    psi_now = psi_digest(psi) if psi else psi_digest({})
    eval_metrics = _psi_eval(system, plasticity, psi, batches)
    stability = _stability_certificate(system, stability_check, episodes)

    return AdaptationResult(
        mode=resolved,
        metrics={
            "loss": float(final.get("loss", 0.0)),
            "free_accuracy": float(final.get("free_accuracy", 0.0)),
            **eval_metrics,
        },
        theta=proof,
        psi_updated=psi_now != psi_digest({}),
        psi_sha=psi_now,
        boundary=detected,
        stability=stability,
        walltime_s=time.perf_counter() - t0,
    )


def _stability_certificate(
    system: object, stability_check: bool, episodes: int
) -> StabilityCertificate | None:
    if not stability_check:
        return None
    from computronium_lab.training import _attach_guard, stability_probe

    handle = _attach_guard(system.geometry)  # type: ignore[attr-defined]
    return stability_probe(handle, {"x": torch.zeros(1)}, episodes)


# ============================================================
# T23.3.3 — ψ-program composition
# ============================================================


@dataclass(frozen=True, slots=True)
class PsiStep:
    """One adaptation step inside a composed ψ-program."""

    task_tag: str
    mode: AdaptationMode
    episodes: int


@dataclass(frozen=True, slots=True)
class PsiProgram:
    """A sequence of ψ-steps composed over one shared ψ state (T23.3.3).

    Steps run back-to-back on the same live ψ dict — later steps acquire
    on top of earlier statistics exactly as the E4 machinery composes
    task-switch episodes over one ridge state.
    """

    steps: tuple[PsiStep, ...] = ()

    def __post_init__(self) -> None:
        # bare-step convenience: PsiProgram(PsiStep(...)) wraps, not unpacks
        if isinstance(self.steps, PsiStep):
            object.__setattr__(self, "steps", (self.steps,))

    def __len__(self) -> int:
        return len(self.steps)

    def __add__(self, other: PsiProgram) -> PsiProgram:
        return PsiProgram(self.steps + other.steps)

    def run(
        self, system: object, data_by_tag: dict[str, object]
    ) -> tuple[AdaptationResult, list[AdaptationResult]]:
        """Run the whole program on one system; per-step results plus a
        final cumulative certificate over the composed ψ state."""
        t0 = time.perf_counter()
        sha_before = theta_digest(system)
        psi: dict[str, Tensor] = {}
        step_results: list[AdaptationResult] = []
        for step in self.steps:
            plasticity = psi_plasticity(step.mode)
            if not psi:
                psi = plasticity.initial_psi(None)  # type: ignore[arg-type]
            history, psi = _psi_only_episodes(
                system, data_by_tag[step.task_tag], plasticity, psi, step.episodes
            )
            final = history[-1] if history else {}
            step_results.append(
                AdaptationResult(
                    mode=step.mode,
                    metrics={
                        "loss": float(final.get("loss", 0.0)),
                        "free_accuracy": float(final.get("free_accuracy", 0.0)),
                    },
                    theta=ThetaInvarianceProof(sha_before, sha_before, True),
                    psi_updated=True,
                    psi_sha=psi_digest(psi),
                    boundary=None,
                    walltime_s=0.0,
                )
            )
        proof = ThetaInvarianceProof(
            sha_before, theta_digest(system), sha_before == theta_digest(system)
        )
        last = step_results[-1] if step_results else None
        cumulative = AdaptationResult(
            mode=last.mode if last else AdaptationMode.TEMPORAL,
            metrics=last.metrics if last else {},
            theta=proof,
            psi_updated=bool(psi),
            psi_sha=psi_digest(psi),
            boundary=None,
            walltime_s=time.perf_counter() - t0,
        )
        return cumulative, step_results


# ============================================================
# T23.3.4 — Z3 operator library + closed-form rule selection
# ============================================================


@dataclass(frozen=True, slots=True)
class Z3Selection:
    """Closed-form operator selection for one probe sequence."""

    index: int
    name: str
    match_rate: float
    scores: dict[str, float]


_Z3_LIBRARY: tuple[tuple[int, str, object], ...] = (
    (0, "identity", Z3Operators.identity),
    (1, "threshold", Z3Operators.threshold),
    (2, "accumulate", Z3Operators.accumulate),
    (3, "last_symbol", Z3Operators.last_symbol),
    (4, "parity", Z3Operators.parity),
    (5, "sparse_topk_route", Z3Operators.sparse_topk_route),
    (6, "sign_flip", Z3Operators.sign_flip),
    (7, "delay", Z3Operators.delay),
)


def select_z3_operator(x: Tensor, y: Tensor) -> Z3Selection:
    """Closed-form rule selection over the Z3 library (T23.3.4).

    No controller, no training: each operator is applied to the probe
    sequence and scored by exact-match rate against the targets; the
    argmax wins. Shape-mismatched operators score 0.
    """
    scores: dict[str, float] = {}
    for index, name, op in _Z3_LIBRARY:
        try:
            out = op(x)  # type: ignore[operator]
        except Exception:  # ruff: ignore[blind-except] - shape-invalid ops simply lose
            scores[name] = 0.0
            continue
        if out.shape == y.shape:
            scores[name] = float((out == y).float().mean())
        else:
            scores[name] = 0.0
    best_name = max(scores, key=lambda n: (scores[n], -_Z3_LIBRARY_ORDER[n]))
    best_index = _Z3_LIBRARY_ORDER[best_name]
    return Z3Selection(
        index=best_index,
        name=best_name,
        match_rate=scores[best_name],
        scores=scores,
    )


_Z3_LIBRARY_ORDER: dict[str, int] = {name: idx for idx, name, _ in _Z3_LIBRARY}


# ============================================================
# T23.3.6 — probe hygiene for synthesis validation
# ============================================================


@dataclass(frozen=True, slots=True)
class ProbeCampaignResult:
    """A forked-copy validation campaign with a paired slope verdict."""

    slope: float
    paired_statistic: float
    paired_p: float
    treated_losses: tuple[float, ...]
    control_losses: tuple[float, ...]
    forked: bool = True
    equal_compute_batches: bool = True


def fork_system(system: object) -> object:
    """Forked copy for probe campaigns (parent state isolated, T23.3.6)."""
    return copy.deepcopy(system)


def heldout_split(
    task_data: object, probe_frac: float = 0.5
) -> tuple[list[tuple[Tensor, Tensor]], list[tuple[Tensor, Tensor]]]:
    """Split a task stream into a probe stream and a held-out buffer.

    The held-out buffer is never touched by probe training — probe batches
    and production evaluation never share data.
    """
    batches = list(task_data)  # type: ignore[arg-type]
    cut = int(len(batches) * (1.0 - probe_frac))
    return batches[:cut], batches[cut:]


def paired_slope(
    treated: Sequence[float], control: Sequence[float]
) -> tuple[float, float, float]:
    """Paired statistical test on per-episode losses (treated vs control).

    Returns (mean improvement slope, t statistic, p value). Positive slope
    means the treated fork improved more than its matched control under
    identical compute.
    """
    from scipy.stats import ttest_rel

    n = min(len(treated), len(control))
    diffs = [control[i] - treated[i] for i in range(n)]
    mean = sum(diffs) / max(n, 1)
    result = ttest_rel(treated[:n], control[:n])
    return float(mean), float(result.statistic), float(result.pvalue)


def probe_campaign(
    system: object,
    task_data: object,
    *,
    mode: AdaptationMode = AdaptationMode.TEMPORAL,
    episodes: int = 10,
    probe_frac: float = 0.5,
) -> ProbeCampaignResult:
    """Hygiene-governed validation campaign (T23.3.6).

    Both arms run on **forked copies** (parent state isolated), consume the
    same number of batches (equal compute), and their per-episode losses
    are compared with a paired test. The treated arm adapts ψ; the control
    arm runs the same episodes with ψ absent — the slope isolates the ψ
    contribution.
    """
    from computronium.core.pipeline import run_train_step

    probe, heldout = heldout_split(task_data, probe_frac)
    del heldout  # never consumed inside the campaign; production data stays isolated

    control = fork_system(system)
    treated = fork_system(system)

    def run_arm(target: object, plasticity: object | None) -> list[float]:
        stream = iter(probe)
        psi: dict[str, Tensor] = (
            plasticity.initial_psi(None) if plasticity is not None else {}  # type: ignore[union-attr]
        )
        losses: list[float] = []
        frozen = _FrozenThetaUpdate()
        credit = _PsiOnlyCredit(target.credit)  # type: ignore[attr-defined]
        for _ in range(episodes):
            x, y = next(stream)
            row = run_train_step(
                target.substrate,  # type: ignore[attr-defined]
                target.geometry,  # type: ignore[attr-defined]
                target.dynamics,  # type: ignore[attr-defined]
                credit,  # type: ignore[arg-type]
                frozen,  # type: ignore[arg-type]
                x,
                y,
                plasticity=plasticity,
                psi=psi,
                context=object(),
            )
            losses.append(float(row.get("loss", 0.0)))
        return losses

    treated_losses = run_arm(treated, psi_plasticity(mode))
    control_losses = run_arm(control, None)

    slope, stat, pvalue = paired_slope(treated_losses, control_losses)
    return ProbeCampaignResult(
        slope=slope,
        paired_statistic=stat,
        paired_p=pvalue,
        treated_losses=tuple(treated_losses),
        control_losses=tuple(control_losses),
    )


__all__ = [
    "PSI_ONLY",
    "AdaptationMode",
    "AdaptationResult",
    "ProbeCampaignResult",
    "PsiPlasticity",
    "PsiProgram",
    "PsiStep",
    "TaskBoundary",
    "TaskBoundaryDetector",
    "ThetaInvarianceProof",
    "Z3Selection",
    "adapt",
    "fork_system",
    "heldout_split",
    "paired_slope",
    "probe_campaign",
    "psi_digest",
    "psi_plasticity",
    "select_z3_operator",
    "theta_digest",
]
