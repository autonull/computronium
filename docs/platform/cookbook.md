# Computronium Cookbook — The Generative Lab API (TODO23)

The Lab API maps **constraints → mechanism → certified result → deployed
artifact**. You specify the problem; the synthesis engine picks the learning
mechanism from the 6-axis ontology and justifies the choice.

```python
from computronium_lab import Lab, Constraints

lab = Lab(seed=0)

spec = lab.specify(
    task="classification",
    dataset="synthetic",
    constraints=Constraints(
        substrate="digital",     # digital | memristive | neuromorphic | photonic | quantum
        precision="float32",
        local_credit=False,      # False → backprop-family allowed
        continual=False,
        memory_gb=8,
        latency_ms=50,
    ),
    objectives=("accuracy", "stability"),
    input_dim=32,
    num_classes=4,
)

result = lab.synthesize(spec)
print(result.provenance)          # why this coordinate: filter → model → card → tree
system = result.build(spec)
```

## 2. Train with guarantees

Every guarantee is opt-in; the result carries certificates, not just metrics.

```python
from computronium_lab import TrainOptions

options = TrainOptions(
    stability_guard=True,      # calibrated kill switch (raises StabilityGuardKill)
    harvest=True,              # EMA weight resurrection
    ceec_logging=True,         # per-epoch evidence into the ledger (needs Lab(record_ledger=...))
    determinism_seal=True,     # bitwise reproducibility proof (2× cost)
)
training = lab.train(system, epochs=3, spec=spec, options=options)
print(training.metrics, training.determinism.verified)
```

## 3. Continual adaptation (frozen θ)

ψ-only adaptation keeps θ bitwise-identical; the proof ships in the result.

```python
adapted = lab.adapt(system, task_data, mode="temporal", episodes=8)
print(adapted.theta.bitwise_invariant, adapted.psi_updated)
```

Modes: `temporal`, `conflict_adaptive`, `closed_form`, `role_split`
(the D22 margin-swap channel: role-split *replaces* the readout role).

## 4. Explore the mechanism space

```python
frontier = lab.explore(spec)      # non-dominated options over spec.objectives
for opt in frontier:
    print(opt.name, opt.predicted_viability, opt.metrics)
```

## 5. Deploy to hardware

```python
artifact = lab.export(
    system, "exports",
    spec=spec,
    target="onnx",
    quantization="ternary",       # None | "int8" | "ternary" (STE)
    input_shape=(1, 32),
)
print(artifact.substrate_report.fidelity_max_abs_diff)
print(artifact.energy)            # tier-labeled: simulated | estimated
```

The manifest JSON is the authoritative artifact: substrate constraints,
fidelity vs digital baseline, quantization note, MAC energy estimate, and
the per-target toolchain descriptor (onnx/pt2/triton/hls/nxsdk/dsl/spice/qasm).
For an edge endpoint: `lab.serve(system, spec=spec, port=8000)`.

## 6. Compare + benchmark

```python
results = lab.compare(["backprop_mlp", "ff_mlp"], epochs=2)
print(lab.report("report.md"))

from computronium_lab import run_benchmark, report_json
bench = run_benchmark(["backprop_mlp", "ff_mlp"], epochs=2)
print(bench.frontier)             # non-dominated over (accuracy↑, walltime↓)
report_json(bench, "bench.json")
```

## Framework adapters (optional installs)

- `HuggingFaceCallback` — records per-epoch loss history, optional JSON
  evidence dump (`uv add transformers`).
- `LightningStabilityCallback` — calibrated stability guard per epoch;
  requires `pl_module.system` (`uv add lightning`).

Both lazy-import their framework and raise a clear install hint otherwise.

## Reading the certificates

| Certificate | Meaning |
|---|---|
| `StabilityCertificate` | guard checked; `max_statistic` vs calibrated τ |
| `HarvestCertificate` | EMA resurrection weights finalized |
| `DeterminismSeal` | same seed → bitwise-identical params + metrics |
| `ThetaInvarianceProof` | SHA-256 before/after — θ untouched during ψ-adaptation |
| `SubstrateReport` | substrate constraints applied; fidelity vs digital |
| `EnergyEstimate` | MAC count × per-device coefficient, tier-labeled |

## Notes

- Catalog Pareto metadata are transcribed from recorded results; synthesis
  never launches probes (TODO23 §11).
- `lab.export` applies substrate constraints **in place**; deepcopy the
  system first if the trained weights must survive.
- Exploration budget: when the top candidate's predicted viability < 0.7 the
  synthesis is exploratory and consumes the per-spec budget; exhaustion is a
  registered CEEC gate (`ExplorationBudgetExhausted`).
