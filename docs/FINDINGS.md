# Findings this project owns

The discovery output to date. Three results survived the project's own audits;
two are negative and one is methodological. Numbers are quoted from their
documents, never recomputed here, and each names the lock or audit that makes
it checkable. A finding leaves this page when its document is retracted, in the
same commit.

| Result | Number | Status | Document |
|---|---|---|---|
| **Deep EqProp boundary** | Vanishing contrastive signal: slope −1.19, R²=0.80 at β=0.01. DirectedEP restores the signal (slope +0.16, R²=0.85) but not accuracy: 9.2% at depth ≥3 — chance for 10 classes. | **G2 FAILED**; 1-layer EqProp remains viable | [`docs/eqprop_deep_limitation.md`](eqprop_deep_limitation.md) |
| **Phantom-knob audit** | A search key sampled by a sweep but silently dropped at construction poisons parity and liveness identically. | Detected by `construction.phantom_knobs`; enforced by `validate_all_rule_spaces()` | [`docs/phantom_knob_audit.md`](phantom_knob_audit.md) |
| **ρ(J) vs σ_max conflation** | Power iteration reported as "spectral radius" on a nonnormal J converged to ≈0.5 while ‖J‖₂ ≈ 10.025. | Caught by `test_jacobian_amplification`; replaced by three separated estimators; old frontier numbers flagged `requires_rerun` | [`docs/CORRECTIONS.md`](CORRECTIONS.md) |

A project that shows its own refuted hypothesis is more credible than one that
shows only a favourable run. [Status and
scope](../README.md#status-and-scope) in the README names everything that is
designed or planned but not yet built; this page names what survived audit,
which is a shorter and more interesting list.

The fourth entry is the one this project did not get to report as a win: the
deep-equilibrium-propagation boundary was the motivating experiment, and the
measurement says multi-layer vanilla EqProp does not learn. DirectedEP restores
the signal and not the accuracy. The honest statement is that the mechanism
boundary now has a diagnosis — composition-error compounding — which is worth
more than a favourable number.
