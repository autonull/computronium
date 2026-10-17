# Demo — one entry point, seven beats

Six minutes, CPU only, no network. Every command below is executed by
`tests/acceptance/test_demo_script.py`; the recording cannot drift from the
software.

Cold open on the README's first screen. One sentence of motivation: *we can
compare learning rules under a protocol none of their authors controls*.

## Beat 0 — the machine is ready

Say: *"Nothing is downloaded and nothing needs a GPU."*

```bash
uv run python -c "import optuna, scipy, torchvision, duckdb; print('ready')"
```

## Beat 1 — the declared space, priced

Say: *"Four arms. Five of six axes held fixed; only the credit rule varies."*

```bash
uv run comp run demo --dry-run
```

Expected excerpt (4 legal cells, budget never binds):

```
axis credit: 4 — gradient, random_projections, pepita, local_goodness
first 4 legal cell(s):
  cell 1: ... credit=gradient, update=adam [geometry.hidden_dim=32]
declared cells: 4  legal: 4
budget: never binds — the space ends first
```

## Beat 2 — execution, and the control

Say: *"The gradient control must clear chance before any comparison is
published. If it does not, the run is invalid — a defect, not a result."*

```bash
uv run comp demo --store demo.duckdb
```

The orchestrator runs beats 1–6. Beat 2 measures 4 arms × 5 seeds = 20 records
in ~30 s and prints the control check:

```
positive control: gradient val_acc=0.4389 vs chance=0.10 (floor 0.30)
```

## Beat 3 — the ledger

Say: *"The store is the checkpoint. A relaunch measures only what the run has
not."*

```bash
uv run comp status --store demo.duckdb
```

## Beat 4 — the governed result

Say: *"A claim carries n and variance. An underpowered comparison is
`INSUFFICIENT`, not 'no effect'. And here is the price of a real answer: 63
seeds per group for a d=0.5 effect, times every arm, times every axis."*

```bash
uv run comp report --store demo.duckdb --format text
```

Expected lines:

```
Claim-Eligible Cells: 4
Claims (n and variance are mandatory; a claim line is not prose):
  credit=pepita: val_acc=0.5417 ±0.0720 (n=5, cells=1)
Limitations (every line re-derivable from a record):
  [insufficient_power] 4 of 4 cell(s) have fewer than the 63 seeds needed ...
  [unpreregistered_claim] ... exploratory comparison, not a confirmatory one
Per-Axis Ablation Tables:
  Credit Ablation [group 1, fixed: substrate=digital, geometry=feedforward, ...]:
      random_projections: mean=0.0961, std=0.0207, n=5 [at chance]
```

## Beat 5 — what is unreached

Say: *"Coverage is the honest map of what this store has not measured."*

```bash
uv run comp coverage report --store demo.duckdb
```

## Beat 6 — what we learned

Three results, quoted from their documents, never recomputed for the video:

1. **Deep EqProp boundary** — `docs/eqprop_deep_limitation.md`. Multi-layer
   vanilla EqProp does not learn: vanishing contrastive signal, slope −1.19,
   R²=0.80 at β=0.01. DirectedEP restores the signal but not accuracy — 9.2% at
   depth ≥3, chance for 10 classes. Gate **G2 FAILED**. Locked by the B2
   autopsy (`test_jacobian_amplification` is the sibling lock for result 3).
2. **Phantom-knob audit** — `docs/phantom_knob_audit.md`. A search key sampled
   by a sweep and dropped at construction poisons parity and liveness
   identically; detected by `computronium.core.construction.phantom_knobs` and
   enforced by `validate_all_rule_spaces()`.
3. **ρ(J) vs σ_max conflation** — `docs/CORRECTIONS.md`. Power iteration
   reported as "spectral radius" on a nonnormal J converged to ≈0.5 while
   ‖J‖₂ ≈ 10.025; caught by `test_jacobian_amplification`, replaced by three
   separated estimators, old frontier numbers flagged `requires_rerun`.

Close: *"This is a laboratory, not a result. Every stronger claim is a ledger
row with a name."*
