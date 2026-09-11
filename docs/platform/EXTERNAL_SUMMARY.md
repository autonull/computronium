# External Summary

Computronium is a research platform for composing and validating
alternative learning mechanisms. This summary is for external audiences:
ML engineers, researchers, and hardware-oriented readers.

## What exists today

Five installable packages (uv workspace under `packages/`):

1. **ceec-core** — a standalone epistemic governance engine: an append-only
   SQLite ledger of artifacts, evidence, beliefs, experiments, and
   decisions, with promotion/boundary gates, calibration tracking, and an
   audit CLI. Use it to make your own experimentation auditable.
2. **psi-peft** — frozen-backbone task switching. A lightweight ψ readout
   accumulates trace-decayed ridge statistics; task conflicts switch
   forgetting on adaptively; a buffered variant amortizes the solve. The
   backbone is bitwise untouched.
3. **local-feedback** — adaptive feedback projections for local learning:
   the feedback matrix slowly blends toward the forward weight, improving
   hidden-layer credit without a global backward pass.
4. **stability** — a calibrated stability guard (`attach(model)`) that kills
   runaway settling dynamics with ROC-calibrated thresholds, plus stable
   matrix constructions with verified spectra.
5. **computronium-lab** — a high-level API over the 6-axis ontology
   (substrate × geometry × dynamics × credit × update × objective): one-line
   composition, presets, `compare()` tables, and validated mechanism
   recipes.

## What was validated (and where it applies)

All results are from CPU simulation on quick synthetic tasks, ≥3 seeds,
against matched baselines. Highlights:

- ψ task switching reaches 0.66–0.74 switching accuracy where a frozen
  null baseline sits at 0.25, with 9× less adaptation walltime than SGD
  readout retraining on the same budget; θ invariant in all ψ arms.
- Adaptive feedback beats matched fixed feedback on all seeds for
  late-trajectory improvement-per-norm (short and medium horizons), with
  alignment 0.95 vs 0.43 — the validated setting is the slow blend.
- Role-split muon-on-readout beats both parent update rules on the mlp task
  (X-USU-001).
- Stable-transient coordinates (ρ ≤ 0.95, σ_max > 1) settle within budget
  and give 4×–2600× transient signal retention over matched contractive
  coordinates — but amplify noise at the same rate (retention gain, not
  SNR gain).

The recipe book (`MECHANISM_RECIPES.md`) carries each mechanism's scope,
limitations, and evidence references. The edge blueprint
(`NEUROMORPHIC_EDGE_BLUEPRINT.md`) maps mechanisms to hardware properties —
simulation only.

## What is deliberately NOT here

- No claim that local learning replaces backpropagation.
- No transformer/LM or large-scale benchmark evidence.
- No physical hardware validation.
- Routing-sparsity efficiency work is blocked pending a learnable dense
  baseline (X-RSE); the boundary is recorded rather than a recipe shipped.

## How to try it

```bash
uv sync --dev --all-extras          # installs all packages as workspace editables
uv run python packages/psi-peft/examples/task_switching_demo.py
uv run python packages/computronium-lab/examples/lab_quickstart.py
```

Each package README has a scoped quickstart; every demo runs on CPU in
under 2 minutes with a fixed seed.