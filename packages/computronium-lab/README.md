# computronium-lab

High-level API over the Computronium 6-axis ontology — compose, train,
compare, and report learning-system coordinates in a few lines. Wraps the
existing validated factories (`computronium.core.presets`, the extracted
mechanism packages) only; no new ontology semantics.

## Install

```bash
uv sync --dev --all-extras   # from the Computronium repo (workspace member)
```

## Usage

```python
from computronium_lab import Lab

lab = Lab(quick=True)              # quick mode: synthetic task, small dims
system = lab.compose("eqprop_mlp") # one-line 5-D composition
metrics = lab.train(system, task="synthetic", epochs=5)
results = lab.compare(["backprop_mlp", "eqprop_mlp", "fa_mlp"], epochs=5)
lab.report("report.md")            # markdown table of the last compare
```

## Presets

Ontology system presets (wrap `computronium.core.presets` factories):
`backprop_mlp`, `eqprop_mlp`, `fa_mlp`, `ff_mlp`, `pepita_mlp`,
`role_split_muon_readout`.

Mechanism recipe presets (delegate to `lab.recipe`):
`temporal_psi_task_switcher`, `adaptive_local_feedback`.

Preset defaults are quick-tuned (32-dim inputs, 4 classes, small MLPs) —
notably `fa_mlp` uses `lr=0.05` because the internal default `0.001` makes
no progress on the quick task inside a few epochs.

## Recipes

`lab.recipe(name)` instantiates validated mechanisms from the extracted
packages: `temporal_psi` (packages/psi-peft; X-TPC-001..003),
`adaptive_feedback` (packages/local-feedback; X-ALI-001/002),
`role_split_muon_readout` (role-split update; X-USU-001). Each recipe
carries summary, when-to-use / when-not guidance, and evidence references.

## CEEC evidence recording (optional, off by default)

```python
lab = Lab(record_ledger="scratch/ceec.sqlite3")
results = lab.compare([...])   # records one 'vector' evidence row
```

## Demos

```bash
python examples/lab_quickstart.py           # compare 3 presets, write report
python examples/mechanism_recipes_demo.py   # temporal ψ, adaptive feedback, role-split
```

## Validated scope

- Quick synthetic gaussian-blob task, CPU, small MLPs; per-preset training is
  deterministic under `Lab(seed=...)` (compose and train each reseed).
- Presets wrap existing validated factories; role-split uses
  `compose_system_from_configs` with the X-USU-001 winner configuration.
- `Lab.compare` at 5 quick epochs: backprop 0.77, eqprop 0.79, fa (lr=0.05)
  0.48 — relative ordering consistent with the internal validation tracks.

## Known limitations

- Quick task is synthetic; MNIST/dataset wiring is not exposed by the Lab
  quick mode yet.
- EqProp needs ≥5 quick epochs to beat chance; 1-epoch results reflect
  initialization quality, not mechanism quality.
- Reports are markdown tables only; no plotting/dashboard (non-goal).
- The Lab adds no new ontology semantics; limits of each mechanism carry
  over from their packages (see package READMEs).

## Evidence references

- Mechanism recipes reference their ledger evidence (X-TPC-*, X-ALI-*,
  X-USU-001); preset comparisons are recorded as lab-scoped evidence only
  when `record_ledger` is set.
- Verification level: smoke-tested quick-mode composition/training with
  determinism checks; no new mechanism claims.