# SEC map — the census of learning primitives

Version SEC-v3, updated 2026-11-20T18:36:01.169582+00:00. 75 primitives, 73 available, all rows at one base box:

`mnist · 32 samples/step · 375 batches · 1 epoch · 150000 ceiling · control 0.8884 · bar 0.1060`

Generated from `results/sec/map.json`; regenerate with `uv run python -m computronium.experiment.documentation.sec_map --map results/sec/map.json --out docs/sec/map.md`. Do not edit by hand.

## Inventory

| axis | measured | unimplemented | defective | refused |
|---|---|---|---|---|
| credit | 16 | 0 | 0 | 3 |
| dynamics | 6 | 0 | 0 | 2 |
| geometry | 6 | 1 | 0 | 5 |
| plasticity | 3 | 0 | 0 | 5 |
| substrate | 4 | 0 | 0 | 6 |
| update | 13 | 0 | 0 | 5 |
| **total 75** | 48 | 1 | 0 | 26 |

## Census (the method cards)

Each row is a method card: its box, ruler, control, number and replay
hash. A card is a result only when its row is measured.

| primitive | status | binding | task | val_acc | seconds | replay |
|---|---|---|---|---|---|---|
| primitive.credit_assignment.eligibility_prop | refused | — | mnist | — | — | — |
| primitive.credit_assignment.forward_tangent | measured | bound | mnist | 0.1302 | 12.279… | 2b7c40b43ab7… |
| primitive.credit_assignment.gradient | measured | bound | mnist | 0.8943 | 4.3890… | 84453097d227… |
| primitive.credit_assignment.homeostatic | measured | inert | mnist | 0.0533 | 4.3551… | 12b56ee1c98b… |
| primitive.credit_assignment.hybrid | measured | bound | mnist | 0.6769 | 4.5759… | b30c50fd568e… |
| primitive.credit_assignment.local_contrastive | measured | bound | mnist | 0.1257 | 7.3038… | 809a15778370… |
| primitive.credit_assignment.local_goodness | measured | bound | mnist | 0.3256 | 4.7769… | 9e94022d0668… |
| primitive.credit_assignment.local_supervision | measured | bound | mnist | 0.7805 | 4.6022… | d541234b8258… |
| primitive.credit_assignment.pc_alm | measured | bound | mnist | 0.0968 | 4.0069… | 60f6a97a5289… |
| primitive.credit_assignment.pepita | measured | bound | mnist | 0.8866 | 4.9534… | 5e2447b53e69… |
| primitive.credit_assignment.random_projections | measured | bound | mnist | 0.1019 | 4.4653… | f632773be0f7… |
| primitive.credit_assignment.rtrl_reference | refused | — | mnist | — | — | — |
| primitive.credit_assignment.score_function | measured | bound | mnist | 0.7180 | 5.0481… | 2d24cd84b952… |
| primitive.credit_assignment.surrogate | measured | bound | mnist | 0.9030 | 6.7866… | 1e07446ef38e… |
| primitive.credit_assignment.target_inversion | measured | bound | mnist | 0.1032 | 4.4326… | 0c739e2b2135… |
| primitive.credit_assignment.temporal_trace | measured | inert | mnist | 0.0968 | 4.6830… | 419ebd8d8413… |
| primitive.credit_assignment.thermodynamic_contrast | measured | bound | mnist | 0.7056 | 12.856… | 526fcd184bfd… |
| primitive.credit_assignment.unbiased_rtrl | refused | — | mnist | — | — | — |
| primitive.credit_assignment.zeroth_order | measured | bound | mnist | 0.1444 | 11.983… | f138b96245e7… |
| primitive.state_dynamics.diffusion | refused | — | mnist | — | — | — |
| primitive.state_dynamics.energy_minimization | measured | bound | mnist | 0.8709 | 22.706… | b74c7d122abd… |
| primitive.state_dynamics.error_predictive_coding | measured | bound | mnist | 0.0982 | 11.593… | 17628dc08251… |
| primitive.state_dynamics.instantaneous | measured | inert | mnist | 0.8943 | 5.4456… | 84453097d227… |
| primitive.state_dynamics.lazy | measured | bound | mnist | 0.8705 | 45.515… | 6a10a6d37495… |
| primitive.state_dynamics.pc_alm | measured | bound | mnist | 0.5319 | 23.230… | a9c7fa2a1c0d… |
| primitive.state_dynamics.predictive_settling | measured | bound | mnist | 0.7096 | 22.905… | 5a59f8347fa4… |
| primitive.state_dynamics.spike_integration | refused | — | mnist | — | — | — |
| primitive.geometry.attention | measured | bound | mnist | 0.9123 | 13.680… | 577a9e38256c… |
| primitive.geometry.causal_transformer | refused | — | mnist | — | — | — |
| primitive.geometry.conv | refused | — | mnist | — | — | — |
| primitive.geometry.feedforward | measured | bound | mnist | 0.8943 | 6.2962… | 84453097d227… |
| primitive.geometry.graph | refused | — | mnist | — | — | — |
| primitive.geometry.nca | measured | bound | mnist | 0.8997 | 13.490… | bddccee8a5c1… |
| primitive.geometry.ntm | refused | — | mnist | — | — | — |
| primitive.geometry.recurrent | refused | — | mnist | — | — | — |
| primitive.geometry.routing | measured | bound | mnist | 0.2519 | 22.665… | 692ee444b12e… |
| primitive.geometry.spatial_lattice | measured | bound | mnist | 0.9050 | 20.371… | 7f4c777f55da… |
| primitive.geometry.tile | unimplemented | bound | mnist | — | 31.890… | 38d5cf0e2874… |
| primitive.geometry.tile_mesh | measured | bound | mnist | 0.7678 | 6.9314… | f75b9471e0c7… |
| primitive.plasticity.closed_form_ridge | measured | bound | mnist | 0.8872 | 7.0281… | a91f48c3a19c… |
| primitive.plasticity.conflict_adaptive | refused | — | mnist | — | — | — |
| primitive.plasticity.fast_weights | refused | — | mnist | — | — | — |
| primitive.plasticity.null | measured | inert | mnist | 0.8943 | 5.5644… | 84453097d227… |
| primitive.plasticity.routing | measured | bound | mnist | 0.8617 | 6.0079… | 56b5e91d0bdd… |
| primitive.plasticity.rule_state | refused | — | — | — | — | — |
| primitive.plasticity.substrate_coupled | refused | — | — | — | — | — |
| primitive.plasticity.temporal_psi | refused | — | mnist | — | — | — |
| primitive.substrate.analog | refused | — | mnist | — | — | — |
| primitive.substrate.complex | refused | — | mnist | — | — | — |
| primitive.substrate.digital | measured | inert | mnist | 0.8943 | 4.5535… | 84453097d227… |
| primitive.substrate.memristive | refused | — | mnist | — | — | — |
| primitive.substrate.neuromorphic | refused | — | mnist | — | — | — |
| primitive.substrate.noisy | measured | inert | mnist | 0.8844 | 4.5884… | 5e1ef4762510… |
| primitive.substrate.optical | refused | — | mnist | — | — | — |
| primitive.substrate.quantum | refused | — | mnist | — | — | — |
| primitive.substrate.sparse | measured | inert | mnist | 0.8831 | 22.780… | ad9c846f7ed3… |
| primitive.substrate.ternary | measured | inert | mnist | 0.8624 | 10.660… | 13072d764474… |
| primitive.parameter_update.adafactor | measured | inert | mnist | 0.3613 | 5.5435… | 2495a9c01c33… |
| primitive.parameter_update.adam | measured | inert | mnist | 0.8786 | 5.3254… | fb64ade15259… |
| primitive.parameter_update.bayesian_online | refused | — | mnist | — | — | — |
| primitive.parameter_update.cascade_synapse | refused | — | mnist | — | — | — |
| primitive.parameter_update.elastic_consolidation | refused | — | mnist | — | — | — |
| primitive.parameter_update.euclidean | measured | inert | mnist | 0.8943 | 5.2320… | 84453097d227… |
| primitive.parameter_update.lion | measured | inert | mnist | 0.4749 | 5.2857… | 5bf3ad6e8b80… |
| primitive.parameter_update.local_adam | measured | inert | mnist | 0.7939 | 5.0523… | cd5a3d460f94… |
| primitive.parameter_update.mean_norm | measured | inert | mnist | 0.1032 | 4.8175… | d7332693a53a… |
| primitive.parameter_update.muon | measured | inert | mnist | 0.9504 | 9.2021… | 1dead35be0f0… |
| primitive.parameter_update.natural_gradient | refused | — | mnist | — | — | — |
| primitive.parameter_update.ortho_adam | measured | inert | mnist | 0.9508 | 9.5616… | f49e59905b91… |
| primitive.parameter_update.quantized_adam | measured | inert | mnist | 0.1846 | 5.4539… | 3febf821c8ee… |
| primitive.parameter_update.riemannian_orthogonal | measured | inert | mnist | 0.9504 | 9.1275… | 5b223adcc2e9… |
| primitive.parameter_update.role_split | measured | inert | mnist | 0.9050 | 4.5777… | 6b8cd66e0ad2… |
| primitive.parameter_update.schedule_free | measured | inert | mnist | 0.1028 | 4.8828… | 5cabd65eff16… |
| primitive.parameter_update.spectral_constrained | measured | inert | mnist | 0.5755 | 8.7089… | 4f0d0649feea… |
| primitive.parameter_update.synaptic_intelligence | refused | — | mnist | — | — | — |


### Refused (rule and reopen trigger)
- `primitive.credit_assignment.eligibility_prop` — `primitive.credit_assignment.eligibility_prop` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.credit_assignment.rtrl_reference` — `primitive.credit_assignment.rtrl_reference` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.credit_assignment.unbiased_rtrl` — `primitive.credit_assignment.unbiased_rtrl` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.state_dynamics.diffusion` — cost cap: 60s after 1/9 boxes; last error: run deadline expired before the first epoch completed
- `primitive.state_dynamics.spike_integration` — `primitive.state_dynamics.spike_integration` composes no vision task family (declares neuromorphic, rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.causal_transformer` — `primitive.geometry.causal_transformer` composes no vision task family (declares lm, rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.conv` — cost cap: 60s after 1/24 boxes; last error: run deadline expired before the first epoch completed
- `primitive.geometry.graph` — `primitive.geometry.graph` composes no vision task family (declares graph); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.ntm` — `primitive.geometry.ntm` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.recurrent` — `primitive.geometry.recurrent` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.plasticity.conflict_adaptive` — `primitive.plasticity.conflict_adaptive` composes no vision task family (declares continual); the slice refuses it before it is priced (TODO95 S2)
- `primitive.plasticity.fast_weights` — `primitive.plasticity.fast_weights` composes no vision task family (declares continual, rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.plasticity.rule_state` — RuleStatePlasticity has no modulate(): the standard train step evolves psi but never applies the selected operator, so the post-step geometry is bit-identical to null (TODO92 §3.9, one-step parameter fingerprint).
- `primitive.plasticity.substrate_coupled` — SubstrateCoupledPlasticity is a no-op at the plasticity protocol level (psi = sigma; the substrate owns state evolution), so the standard step is bit-identical to null (TODO92 §3.9, one-step parameter fingerprint).
- `primitive.plasticity.temporal_psi` — `primitive.plasticity.temporal_psi` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.substrate.analog` — `primitive.substrate.analog` composes no vision task family (declares analog, neuromorphic); the slice refuses it before it is priced (TODO95 S2)
- `primitive.substrate.complex` — `primitive.substrate.complex` composes no vision task family (declares analog, quantum); the slice refuses it before it is priced (TODO95 S2)
- `primitive.substrate.memristive` — `primitive.substrate.memristive` composes no vision task family (declares analog, neuromorphic); the slice refuses it before it is priced (TODO95 S2)
- `primitive.substrate.neuromorphic` — `primitive.substrate.neuromorphic` composes no vision task family (declares neuromorphic, rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.substrate.optical` — `primitive.substrate.optical` composes no vision task family (declares analog, photonic); the slice refuses it before it is priced (TODO95 S2)
- `primitive.substrate.quantum` — `primitive.substrate.quantum` composes no vision task family (declares quantum); the slice refuses it before it is priced (TODO95 S2)
- `primitive.parameter_update.bayesian_online` — `primitive.parameter_update.bayesian_online` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.parameter_update.cascade_synapse` — `primitive.parameter_update.cascade_synapse` composes no vision task family (declares continual, rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.parameter_update.elastic_consolidation` — `primitive.parameter_update.elastic_consolidation` composes no vision task family (declares continual); the slice refuses it before it is priced (TODO95 S2)
- `primitive.parameter_update.natural_gradient` — cost cap: 60s after 1/24 boxes; last error: run deadline expired before the first epoch completed
- `primitive.parameter_update.synaptic_intelligence` — `primitive.parameter_update.synaptic_intelligence` composes no vision task family (declares continual); the slice refuses it before it is priced (TODO95 S2)

## Interaction (which axes change together)

The interaction slice is not measured at this box.

## Deep dive (one surprising row, one box)

The deep dive is not measured at this box.

## Adding a primitive (the recipe)

1. Declare the axis spec in its `primitives/<axis>/spec.py`; the registry derives from the specs, never a second list.
2. Add the config classmethod on the axis's config class.
3. Export it from the root `__all__`/`_LAZY` and `ontology/__init__.py`; the wiring lock proves the four surfaces agree.
4. Declare the binding condition in `sec_binding.py`: an axis that does not bind is `inert`, not a result.
5. Run `uv run python -m computronium.experiment.sec_census --out results/sec`, then `comp verify --primitive <id> --slice <family>`; a row without its box, ruler, control or replay hash is refused.

The recipe is a test: `tests/acceptance/test_extension_path.py` adds a credit and holds a map row end to end.
