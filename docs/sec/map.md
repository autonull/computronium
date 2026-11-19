# SEC map — the census of learning primitives

Version SEC-v3, updated 2026-11-19T07:57:17.199589. 75 primitives, 73 available, all rows at one base box:

`mnist · 32 samples/step · 375 batches · 1 epoch · 150000 ceiling · control 0.8908 · bar 0.1060`

Generated from `results/sec/map.json`; regenerate with `uv run python -m computronium.experiment.documentation.sec_map --map results/sec/map.json --out docs/sec/map.md`. Do not edit by hand.

## Inventory

| axis | measured | defect | refused | unmeasured |
|---|---|---|---|---|
| credit | 15 | 1 | 3 | 0 |
| dynamics | 7 | 0 | 1 | 0 |
| geometry | 7 | 5 | 0 | 0 |
| plasticity | 5 | 0 | 3 | 0 |
| substrate | 9 | 0 | 1 | 0 |
| update | 14 | 0 | 4 | 0 |
| **total 75** | 57 | 6 | 12 | 0 |

## Census (the method cards)

Each row is a method card: its box, ruler, control, number and replay
hash. A card is a result only when its row is measured.

| primitive | status | binding | task | val_acc | seconds | replay |
|---|---|---|---|---|---|---|
| primitive.credit_assignment.eligibility_prop | refused | — | mnist | — | — | — |
| primitive.credit_assignment.forward_tangent | measured | bound | mnist | 0.1653 | 11.784… | 1a4194c51a89… |
| primitive.credit_assignment.gradient | measured | bound | mnist | 0.8943 | 5.6883… | af18f50f2969… |
| primitive.credit_assignment.homeostatic | measured | inert | mnist | 0.1348 | 5.7041… | 4d94f5a3e38b… |
| primitive.credit_assignment.hybrid | measured | bound | mnist | 0.7367 | 8.3796… | db70a92ea125… |
| primitive.credit_assignment.local_contrastive | measured | bound | mnist | 0.1989 | 9.2234… | 758454631a6a… |
| primitive.credit_assignment.local_goodness | measured | bound | mnist | 0.3403 | 5.9856… | a49d0bdbfb45… |
| primitive.credit_assignment.local_supervision | measured | bound | mnist | 0.7769 | 5.5402… | 9fc2328e17a5… |
| primitive.credit_assignment.pc_alm | measured | bound | mnist | 0.1224 | 4.3458… | 5bec81312272… |
| primitive.credit_assignment.pepita | measured | bound | mnist | 0.8937 | 6.2525… | ab0ad33346c5… |
| primitive.credit_assignment.random_projections | measured | bound | mnist | 0.1333 | 5.1301… | 590619971fd4… |
| primitive.credit_assignment.rtrl_reference | refused | — | mnist | — | — | — |
| primitive.credit_assignment.score_function | measured | bound | mnist | 0.7316 | 6.4609… | f94f61660f5d… |
| primitive.credit_assignment.surrogate | defect | bound | mnist | — | 8.0996… | fc9fd5fa0f87… |
| primitive.credit_assignment.target_inversion | measured | bound | mnist | 0.1195 | 5.0869… | b30d4fe1a1d9… |
| primitive.credit_assignment.temporal_trace | measured | inert | mnist | 0.1224 | 4.7367… | 9865c34a26f9… |
| primitive.credit_assignment.thermodynamic_contrast | measured | bound | mnist | 0.7817 | 11.224… | dedf77fc8e7c… |
| primitive.credit_assignment.unbiased_rtrl | refused | — | mnist | — | — | — |
| primitive.credit_assignment.zeroth_order | measured | bound | mnist | 0.1665 | 9.7084… | d4f0c67bd8c1… |
| primitive.state_dynamics.diffusion | refused | — | mnist | — | — | — |
| primitive.state_dynamics.energy_minimization | measured | bound | mnist | 0.8786 | 14.808… | 9a675ccf9fbe… |
| primitive.state_dynamics.error_predictive_coding | measured | bound | mnist | 0.1242 | 16.779… | 5fe08e908bdd… |
| primitive.state_dynamics.instantaneous | measured | inert | mnist | 0.8943 | 4.9515… | af18f50f2969… |
| primitive.state_dynamics.lazy | measured | bound | mnist | 0.8775 | 53.886… | abfdbaf6458b… |
| primitive.state_dynamics.pc_alm | measured | bound | mnist | 0.6398 | 41.911… | 522bf2a001ef… |
| primitive.state_dynamics.predictive_settling | measured | bound | mnist | 0.7235 | 15.367… | 6ee66b34d2ad… |
| primitive.state_dynamics.spike_integration | measured | bound | mnist | 0.1324 | 32.518… | 08f4f5b311f9… |
| primitive.geometry.attention | defect | bound | mnist | — | 10.708… | 4016d9b65aa3… |
| primitive.geometry.causal_transformer | defect | bound | mnist | — | 10.346… | 4b2e542b28e1… |
| primitive.geometry.conv | measured | bound | mnist | 0.1217 | 39.564… | fecce0ba9af1… |
| primitive.geometry.feedforward | measured | bound | mnist | 0.8943 | 5.1505… | af18f50f2969… |
| primitive.geometry.graph | defect | bound | mnist | — | — | — |
| primitive.geometry.nca | measured | bound | mnist | 0.8956 | 5.7591… | 1bd52f0d938c… |
| primitive.geometry.ntm | measured | bound | mnist | 0.8758 | 9.4908… | 14be51943004… |
| primitive.geometry.recurrent | measured | bound | mnist | 0.8971 | 39.266… | abc9a85c9fbc… |
| primitive.geometry.routing | defect | bound | mnist | — | 21.956… | 156767743b2f… |
| primitive.geometry.spatial_lattice | measured | bound | mnist | 0.9137 | 34.756… | f678028b5554… |
| primitive.geometry.tile | defect | bound | mnist | — | 45.651… | 459b51eff492… |
| primitive.geometry.tile_mesh | measured | bound | mnist | 0.6899 | 10.283… | 4bb03feb582c… |
| primitive.plasticity.closed_form_ridge | refused | — | mnist | — | — | — |
| primitive.plasticity.conflict_adaptive | measured | bound | mnist | 0.2882 | 18.513… | 70a690f2a5aa… |
| primitive.plasticity.fast_weights | measured | bound | mnist | 0.8918 | 12.854… | 66514bf8a702… |
| primitive.plasticity.null | measured | inert | mnist | 0.8943 | 5.1782… | af18f50f2969… |
| primitive.plasticity.routing | measured | bound | mnist | 0.8681 | 5.4245… | 71cae9157481… |
| primitive.plasticity.rule_state | refused | — | — | — | — | — |
| primitive.plasticity.substrate_coupled | refused | — | — | — | — | — |
| primitive.plasticity.temporal_psi | measured | bound | mnist | 0.8847 | 5.6990… | a67889ddfcf3… |
| primitive.substrate.analog | measured | inert | mnist | 0.8869 | 6.0460… | d9c188bca3b7… |
| primitive.substrate.complex | measured | inert | mnist | 0.8914 | 5.0206… | 3f55dfb4f266… |
| primitive.substrate.digital | measured | inert | mnist | 0.8943 | 5.0767… | af18f50f2969… |
| primitive.substrate.memristive | measured | inert | mnist | 0.8895 | 9.0944… | e9fbe27ce634… |
| primitive.substrate.neuromorphic | measured | inert | mnist | 0.8782 | 17.338… | 3cfbcd417045… |
| primitive.substrate.noisy | measured | inert | mnist | 0.8914 | 5.0280… | dd60ed6d1e43… |
| primitive.substrate.optical | measured | inert | mnist | 0.8898 | 5.5404… | b1c1609dd6da… |
| primitive.substrate.quantum | refused | — | mnist | — | — | — |
| primitive.substrate.sparse | measured | inert | mnist | 0.8850 | 8.0622… | 89c12860aae0… |
| primitive.substrate.ternary | measured | inert | mnist | 0.8713 | 9.5803… | bec3364a3f66… |
| primitive.parameter_update.adafactor | measured | inert | mnist | 0.9330 | 5.7019… | 65b5100d6b28… |
| primitive.parameter_update.adam | measured | inert | mnist | 0.9080 | 5.1859… | 1c6ecca6b2b3… |
| primitive.parameter_update.bayesian_online | refused | — | mnist | — | — | — |
| primitive.parameter_update.cascade_synapse | refused | — | mnist | — | — | — |
| primitive.parameter_update.elastic_consolidation | measured | inert | mnist | 0.6256 | 5.0234… | 215f3863029d… |
| primitive.parameter_update.euclidean | measured | inert | mnist | 0.8943 | 4.9952… | af18f50f2969… |
| primitive.parameter_update.lion | measured | inert | mnist | 0.9265 | 5.2010… | f3a0e28d3106… |
| primitive.parameter_update.local_adam | measured | inert | mnist | 0.7959 | 5.2973… | 735912bfcac5… |
| primitive.parameter_update.mean_norm | measured | inert | mnist | 0.8869 | 5.1152… | afc1eb8af967… |
| primitive.parameter_update.muon | measured | inert | mnist | 0.9489 | 9.8602… | b1cd5cb61b28… |
| primitive.parameter_update.natural_gradient | refused | — | mnist | — | — | — |
| primitive.parameter_update.ortho_adam | measured | inert | mnist | 0.9472 | 10.141… | 0acdb85fae68… |
| primitive.parameter_update.quantized_adam | measured | inert | mnist | 0.1016 | 7.5271… | 5da71d8d64da… |
| primitive.parameter_update.riemannian_orthogonal | measured | inert | mnist | 0.9489 | 10.312… | a85243ebe9ee… |
| primitive.parameter_update.role_split | measured | inert | mnist | 0.9006 | 5.3738… | e7cd99d5abc7… |
| primitive.parameter_update.schedule_free | measured | inert | mnist | 0.9190 | 5.4635… | 54fd01e7c403… |
| primitive.parameter_update.spectral_constrained | measured | inert | mnist | 0.6256 | 11.485… | f0d5b65c5084… |
| primitive.parameter_update.synaptic_intelligence | refused | — | mnist | — | — | — |

### Defects (execution facts, with their mechanism)
- `primitive.credit_assignment.surrogate` — param_count 234898 over ceiling
- `primitive.geometry.attention` — param_count 494986 over ceiling
- `primitive.geometry.causal_transformer` — param_count 397568 over ceiling
- `primitive.geometry.graph` — Training failed: graph node-mode forward got 32 rows for a 2-node static edge index; a batched graph input must pass edge_index and batch, because an unbatched caller feeds node rows to a foreign edge list (an out-of-bounds index on CUDA, a caught warning on CPU)
- `primitive.geometry.routing` — param_count 234898 over ceiling
- `primitive.geometry.tile` — param_count 628280 over ceiling

### Refused (rule and reopen trigger)
- `primitive.credit_assignment.eligibility_prop` — `primitive.credit_assignment.eligibility_prop` composes no vision task family (declares continual, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.credit_assignment.rtrl_reference` — `primitive.credit_assignment.rtrl_reference` composes no vision task family (declares sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.credit_assignment.unbiased_rtrl` — `primitive.credit_assignment.unbiased_rtrl` composes no vision task family (declares sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.state_dynamics.diffusion` — cost cap: 60s after 2/12 boxes; last error: run deadline expired before the first epoch completed
- `primitive.plasticity.closed_form_ridge` — `primitive.plasticity.closed_form_ridge` composes no vision task family (declares continual, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.plasticity.rule_state` — RuleStatePlasticity has no modulate(): the standard train step evolves psi but never applies the selected operator, so the post-step geometry is bit-identical to null (TODO92 §3.9, one-step parameter fingerprint).
- `primitive.plasticity.substrate_coupled` — SubstrateCoupledPlasticity is a no-op at the plasticity protocol level (psi = sigma; the substrate owns state evolution), so the standard step is bit-identical to null (TODO92 §3.9, one-step parameter fingerprint).
- `primitive.substrate.quantum` — `primitive.substrate.quantum` composes no vision task family (declares scientific); the slice refuses it before it is priced (TODO95 S2)
- `primitive.parameter_update.bayesian_online` — `primitive.parameter_update.bayesian_online` composes no vision task family (declares continual, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.parameter_update.cascade_synapse` — `primitive.parameter_update.cascade_synapse` composes no vision task family (declares continual); the slice refuses it before it is priced (TODO95 S2)
- `primitive.parameter_update.natural_gradient` — cost cap: 60s after 1/24 boxes; last error: run deadline expired before the first epoch completed
- `primitive.parameter_update.synaptic_intelligence` — `primitive.parameter_update.synaptic_intelligence` composes no vision task family (declares continual); the slice refuses it before it is priced (TODO95 S2)

## Interaction (which axes change together)

Pair: **credit × dynamics** — status=measured

- levels: {'credit': ['gradient', 'target_inversion'], 'dynamics': ['instantaneous', 'lazy']}
- control val_acc: 0.8908
- effect: 0.0153 [-0.0092, 0.0397] at 3 seeds — a difference in differences

## Deep dive (one surprising row, one box)

Primitive: **primitive.credit_assignment.target_inversion** — verdict=coordinate

- margin over the bar: 0.0135 (val_acc 0.1195)
- knob: `credit.feedback_scale` at its declared default 0.01
- knob binds: False; pair has power: False
- claim: tuning credit.feedback_scale on primitive.credit_assignment.target_inversion moves val_acc by at least 0.01 at the mnist base
- margin 0.01, alpha 0.05, fixed n=5

| factor | knob value | status | val_acc | seconds |
|---|---|---|---|---|
| 0.1× | 0.001 | measured | 0.1195 | 5.1865… |
| 1× | 0.01 | measured | 0.1195 | 5.4925… |
| 10× | 0.1 | measured | 0.1195 | 5.6648… |

Stop: rung 4: the arms are identical at every seed — the knob does not bind at this box, so the pair has no power and is marked, not priced (a capability gap, TODO95 S4).

## Adding a primitive (the recipe)

1. Declare the axis spec in its `primitives/<axis>/spec.py`; the registry derives from the specs, never a second list.
2. Add the config classmethod on the axis's config class.
3. Export it from the root `__all__`/`_LAZY` and `ontology/__init__.py`; the wiring lock proves the four surfaces agree.
4. Declare the binding condition in `sec_binding.py`: an axis that does not bind is `inert`, not a result.
5. Run `uv run python -m computronium.experiment.sec_census --out results/sec`, then `comp verify --primitive <id> --slice <family>`; a row without its box, ruler, control or replay hash is refused.

The recipe is a test: `tests/acceptance/test_extension_path.py` adds a credit and holds a map row end to end.
