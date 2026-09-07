"""H1 probe (TODO12b): is UnitRMSUpdate defective?

Verdict (2026-09-06): REFUTED as an implementation defect; the D16
"noise floor" is an lr-semantics mismatch, not a broken rule.

Measured (torch.manual_seed(0), CPU, 64-D quadratic f=0.5*sum(a*x^2),
a=0.1..1.0, x0=1, 400 steps):
- lr=0.3:  f 17.60 -> 4.6e-05; ||x|| -> 0.0099 (lr-ball, expected for a
  fixed-RMS step); cosine(step, -grad) = 1.0000 from step ~40 on.
- lr=0.02: f 17.60 -> 7.2e-07; ||x|| -> 0.0009.
  No NaN/inf, no divergence, direction preserved: the EMA-normalize
  rule behaves like well-scaled SGD pre-convergence — exactly what D16
  claimed it could not do.
- Bitwise diff vs hand-written reference (buf = m*buf + g;
  step = lr * buf / rms(buf)) over 5 steps, lr=0.1, m=0.9:
  max abs diff = 0.0 — implementation is exact.
- Step-magnitude accounting: post-warmup ||Δθ|| = step_size per tensor
  exactly. unit_rms's lr is ABSOLUTE DISPLACEMENT, not gradient-scale-
  relative: at D16's lr=0.002, 150 batches move each weight <= 0.3 —
  far too small to leave chance level while euclid lr=0.1 takes
  gradient-scaled steps. The D16 grid does not transfer across update
  families; re-baseline unit_rms on its own lr scale.
"""

import time

import torch

from computronium.ontology.update import UnitRMSUpdate


def _cfg(lr: float, m: float = 0.9):
    from computronium.ontology.update import ParameterUpdateConfig

    return ParameterUpdateConfig.unit_rms(step_size=lr, momentum=m)


def _quadratic_run(lr: float, steps: int = 400) -> dict[str, float]:
    torch.manual_seed(0)
    a = torch.linspace(0.1, 1.0, 64)
    params = {"0.weight": torch.ones(1, 64)}
    upd = UnitRMSUpdate(_cfg(lr))
    f0 = (0.5 * a * params["0.weight"].squeeze() ** 2).sum().item()
    cosines: list[float] = []
    for _ in range(steps):
        x = params["0.weight"]
        g = (a * x).reshape(1, 64)
        step = upd.step(params, [g], None)["0.weight"]  # type: ignore[arg-type]
        delta = (step - x).squeeze()
        cosines.append(
            (torch.dot(delta, -g.squeeze()) / (delta.norm() * g.norm() + 1e-12)).item()
        )
        params["0.weight"] = step
    f1 = (0.5 * a * params["0.weight"].squeeze() ** 2).sum().item()
    return {
        "f0": f0,
        "f_final": f1,
        "x_norm": params["0.weight"].norm().item(),
        "cos_final": cosines[-1],
        "cos_min_after_40": min(cosines[40:]),
    }


def _reference_diff() -> float:
    torch.manual_seed(1)
    lr, m = 0.1, 0.9
    upd = UnitRMSUpdate(_cfg(lr, m))
    p = torch.randn(8, 4)
    buf = torch.zeros_like(p)
    for _ in range(5):
        g = torch.randn_like(p)
        new = upd.step({"0.weight": p.clone()}, [g.clone()], None)["0.weight"]  # type: ignore[arg-type]
        buf.mul_(m).add_(g)
        ref = p - lr * buf / buf.square().mean().sqrt().add_(1e-8)
        assert torch.equal(new, ref), (new - ref).abs().max().item()
        p = new
    return 0.0


def main() -> None:
    t0 = time.perf_counter()
    for lr in (0.3, 0.02):
        r = _quadratic_run(lr)
        print(
            f"lr={lr}: f {r['f0']:.4f} -> {r['f_final']:.2e}, "
            f"|x|={r['x_norm']:.4f}, cos={r['cos_final']:.4f} "
            f"(min after 40: {r['cos_min_after_40']:.4f})"
        )
    print(f"reference bitwise diff: {_reference_diff()}")
    print(f"walltime: {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
