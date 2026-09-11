# Mechanism Recipe Book

Validated mechanisms from the Computronium platform, each with scope,
benchmarks, and evidence references. Claims are scoped to the validated
task/budget; nothing here is a universal claim (G-RELEASE-5).

---

## 1. Temporal-ψ task switching (`psi-peft`)

- **What:** a frozen backbone acquires, switches, and re-acquires tasks via a
  lightweight ψ readout with trace-decayed ridge updates; conflict between
  task label geometries switches forgetting on (`AdaptivePsiReadout`), a
  buffered variant amortizes the ridge solve (`BufferedPsiReadout`).
- **When to use:** frozen backbone + changing task heads; conflicting label
  geometry between tasks; no budget for readout retraining.
- **When not to use:** non-conflicting incremental tasks (forgetting stays
  off, which is correct but the adaptive machinery is idle), generative
  modeling, cases requiring backbone adaptation.
- **Snippet:**
  ```python
  from psi_peft import AdaptivePsiReadout
  ro = AdaptivePsiReadout(feature_dim=64, num_classes=4)
  ro.update(h, y)          # trace-decayed ridge accumulate
  logits = ro.forward(h)
  ```
- **Benchmark (quick task, 3 seeds, mean):** frozen_null 0.25; closed-form
  B=0.26 (blends, as X-TPC-002 predicts); temporal_090 B=0.66 / A-retention
  0.76; adaptive B=0.74; SGD readout retraining 9× slower walltime at lower
  quick-budget accuracy. θ bitwise-invariant in all ψ arms.
- **Validated scope:** quick-budget CPU probes on synthetic conflicting task
  pairs; 3 seeds; frozen-feature setting.
- **Limitations:** buffered arm trades ~0.1 conflict-phase accuracy for ~2×
  speed (documented boundary, plan §T20.3.4); no optimality claim vs gradient
  readout retraining; no transformer/LM evidence.
- **Evidence:** X-TPC-001, X-TPC-002, X-TPC-003, X-TAC-001
  (E-000022..E-000026); belief B-H2-TEMPORAL-PSI-CREDIT.

## 2. Adaptive local feedback (`local-feedback`)

- **What:** the feedback projection B drifts slowly toward the normalized
  forward weight (EMA blend, matched norm), making `e @ B` approach true
  backprop through the readout — improving local descent quality without a
  global backward pass.
- **When to use:** local-learning loops (no weight transport) that need
  better hidden-layer credit; matched-norm comparison setups.
- **When not to use:** very short horizons on saturated tasks; zero/degenerate
  forward weights; depth beyond the validated two-layer scope; fast
  re-projection (lr=1.0 thrashes — slow blend is the validated setting).
- **Snippet:**
  ```python
  from local_feedback import AdaptiveFeedback
  fb = AdaptiveFeedback(in_features=32, out_features=4, feedback_lr=0.02)
  dh = fb.project(error)   # hidden credit = dh^T x
  fb.update(W2)            # slow blend toward normalized forward weight
  ```
- **Benchmark (3 seeds × 60 steps, matched norm):** adaptive late
  improvement-per-norm 0.0427±0.004 vs fixed 0.0381±0.004 (per-seed wins
  asserted); feedback alignment 0.95 vs 0.43. X-ALI-002 short-trajectory
  (10 steps): adaptive late ipn 0.88/0.88/0.69 vs fixed 0.49/0.48/0.53.
- **Validated scope:** two-layer local trainer, matched displacement norm,
  slow-blend `feedback_lr=0.02`, 3 seeds.
- **Limitations:** not validated end-to-end against internal EqProp systems;
  depth scaling unvalidated (X-ALI-003 deferred).
- **Evidence:** X-ALI-001 (E-000018), X-ALI-002 (E-000027); belief
  B-H1-ADAPTIVE-LOCAL-INVERSES narrowed to [0.55, 0.85].

## 3. Role-split muon readout (`computronium-lab`)

- **What:** role-split dispatcher — Riemannian-orthogonal (Muon-class)
  update on the readout weight, euclidean elsewhere. X-USU-001 winner: beats
  both parents on the mlp task.
- **When to use:** backprop MLPs where readout orthogonalization rescues
  one-step descent; heterogeneous update budgets (muon-class hardware on the
  readout only).
- **When not to use:** local-credit (FF×Muon) coordinates — the lift
  collapses under Newton–Schulz whitening at width 32.
- **Snippet:**
  ```python
  from computronium_lab import build_recipe
  system = build_recipe("role_split_muon_readout", input_dim=32, hidden_dims=(64, 32))
  metrics = system.train_step(x, y)
  ```
- **Benchmark:** X-USU-001 role-split > each parent rule on the mlp task
  (internal ledger).
- **Validated scope:** backprop MLP, quick task; muon-on-readout only.
- **Limitations:** the muon-on-forward degradation (X-USU-002 defect hunt)
  was explicitly deferred in TODO20 — the boundary above is the X-USU-001
  result, not a defect-hunt conclusion; no boundary declared beyond it.
- **Evidence:** X-USU-001.

## 4. Stable amplification (`stability` + `computronium-lab`)

- **What:** a linear coordinate with realized ρ ≤ limit while σ_max > 1
  (size-4 Jordan blocks, rotated) — transient amplification without
  divergence. `stability.matrices` builds and verifies the spectrum;
  `computronium_lab.build_recipe("stable_amplification")` wraps it.
- **When to use:** short-horizon transient gain at matched spectral radius;
  noisy linear substrates needing fast response while remaining stable.
- **When not to use:** SNR improvement — X-STA-002 shows isotropic noise is
  amplified at the *same* transient rate as the signal (paired replay:
  noise-divergence ratio ≈ retention ratio), so the mechanism buys
  retention, not noise robustness; long-horizon memory (the transient
  decays; settling takes 168–344 steps at ρ=0.85 in the quick family).
- **Snippet:**
  ```python
  from computronium_lab import build_recipe
  amp = build_recipe("stable_amplification", gain=0.85, dim=4)
  y = amp(x)               # x @ W.T, verified rho<=0.95, sigma_max>1
  ```
- **Benchmark (X-STA-002, 3 seeds, horizon 20, paired replay):** signal
  retention vs matched contractive control at ρ=0.85 — 4.2–5.5× at
  σ_max=1.21, 19–40× at σ_max=1.60, 940–2600× at σ_max=4.06; all
  amplifying coordinates settle within the 500-step budget (238–344);
  noise divergence scales with the same ratio (SNR preserved).
- **Validated scope:** linear transitions (J = W measured exactly),
  quick family ρ_t=0.85, c ≤ 4, 3 seeds, paired-replay protocol.
- **Limitations:** linear-coordinate scope only; isotropic-noise SNR
  unchanged; no nonlinear-system evidence.
- **Evidence:** X-STA-001, X-STA-002 (E-000028); belief
  B-H3-STABLE-TRANSIENT-AMPLIFICATION narrowed to [0.55, 0.85].