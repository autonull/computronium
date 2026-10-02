## 8. Evidence & claims

Claims are labeled by verification level (§1) and governed by CEEC ([`packages/ceec-core`](packages/ceec-core)).

| Claim | Level | Evidence |
|---|---|---|
| Seeded axis effect (E3): credit-axis manipulation shifts outcomes, d ≈ −1.5, p < 0.01 | 3 | `scripts/probes/e3_seeded_axis_effect.py` — **measured on `SyntheticGroundTruth`, a constructed response surface, not on a trained system.** This is evidence the analysis machinery detects an effect it was handed. It is not evidence that the system learns. |
| Transfer provenance (E4): provenance-tagged records support transfer, d ≈ −1.52 | 3 | `scripts/probes/e4_transfer_provenance.py` — same constructed surface, same caveat |
| Effect-size protocol (E2) | 2 | conformance evidence audit (46 pass / 42 skip / 0 fail) |
| Kernel orchestration guarantees U1–U5 | 4 | `tests/acceptance/test_unified_kernel.py` — guarantees *orchestration* (policy interchangeability, pause/resume, one store, one measurement identity). **The evaluator behind those tests is currently a placeholder** returning a walltime, so no measurement is actually made; see the kernel-status note below |
| Locked demo blocks (§3, §4) | 4 | `tests/integration/test_demo_compose_6axis.py`, `test_demo_swap_credit.py` — these *do* train and assert real accuracies |
| Conformance audit C1–C88 | 2–3 | `comp conformance` |

The effect-size protocol: seeded, paired comparisons with preregistered objectives from the PRIORS registry; only Level-4/5 measurements may enter Class E claims, and they are reported at measured strength.

---
