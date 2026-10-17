## Findings we own

Three results survived the project's own audits. Numbers are quoted from the
documents, never recomputed here; each names the lock or audit that makes it
checkable.

| Result | Number | Status | Document |
|---|---|---|---|
| Deep EqProp boundary | Vanishing contrastive signal: slope −1.19, R²=0.80 at β=0.01. DirectedEP restores the signal (slope +0.16, R²=0.85) but not accuracy: 9.2% at depth ≥3 — chance for 10 classes. | **G2 FAILED**; 1-layer EqProp remains viable | `docs/eqprop_deep_limitation.md` |
| Phantom-knob audit | A search key sampled by a sweep but silently dropped at construction poisons parity and liveness identically. | Detected by `construction.phantom_knobs`; enforced by `validate_all_rule_spaces()` | `docs/phantom_knob_audit.md` |
| ρ(J) vs σ_max conflation | Power iteration reported as "spectral radius" on a nonnormal J converged to ≈0.5 while ‖J‖₂ ≈ 10.025. | Caught by `test_jacobian_amplification`; replaced by three separated estimators; old frontier numbers flagged `requires_rerun` | `docs/CORRECTIONS.md` |

A project that shows its own refuted hypothesis is more credible than one that
shows only a favourable run. These three are the discovery output to date; the
readiness ledger below names everything that is designed or planned but not
built.
