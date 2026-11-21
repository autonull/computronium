# SEC map — the census of learning primitives

Version SEC-v3, updated 2026-11-21T09:28:15.997948. 75 primitives, 73 available, all rows at one base box:

`mnist · 32 samples/step · 375 batches · 1 epoch · 150000 ceiling · control 0.8884 · bar 0.1060`

Generated from `results/sec/map.json`; regenerate with `uv run python -m computronium.experiment.documentation.sec_map --map results/sec/map.json --out docs/sec/map.md`. Do not edit by hand.

## Inventory

| axis | measured | unimplemented | defective | refused |
|---|---|---|---|---|
| credit | 16 | 0 | 0 | 3 |
| dynamics | 7 | 0 | 0 | 1 |
| geometry | 5 | 0 | 1 | 6 |
| plasticity | 3 | 0 | 0 | 5 |
| substrate | 4 | 0 | 0 | 6 |
| update | 13 | 0 | 0 | 5 |
| **total 75** | 48 | 0 | 1 | 26 |

## Census (the method cards)

Each row is a method card: its box, ruler, control, number and replay
hash. A card is a result only when its row is measured.

| primitive | status | binding | task | val_acc | seconds | replay |
|---|---|---|---|---|---|---|
| primitive.credit_assignment.eligibility_prop | refused | — | mnist | — | — | — |
| primitive.credit_assignment.forward_tangent | measured | bound | mnist | 0.1302 | 14.481… | 7de84eb23192… |
| primitive.credit_assignment.gradient | measured | bound | mnist | 0.8844 | 5.1272… | b4bf1ebd0894… |
| primitive.credit_assignment.homeostatic | measured | inert | mnist | 0.0533 | 5.5443… | 97378f0de6a5… |
| primitive.credit_assignment.hybrid | measured | bound | mnist | 0.6769 | 5.2690… | 30428a72ae36… |
| primitive.credit_assignment.local_contrastive | measured | bound | mnist | 0.1257 | 8.5011… | 564222ba25e9… |
| primitive.credit_assignment.local_goodness | measured | bound | mnist | 0.3256 | 5.0953… | 16153ce10f52… |
| primitive.credit_assignment.local_supervision | measured | bound | mnist | 0.7805 | 6.2717… | f3d707dd10e1… |
| primitive.credit_assignment.pc_alm | measured | bound | mnist | 0.5319 | 24.604… | 2a5de00f4ba6… |
| primitive.credit_assignment.pepita | measured | bound | mnist | 0.8866 | 7.3437… | b51ab4672dd1… |
| primitive.credit_assignment.random_projections | measured | bound | mnist | 0.1019 | 4.9525… | 72d9be805ea0… |
| primitive.credit_assignment.rtrl_reference | refused | — | mnist | — | — | — |
| primitive.credit_assignment.score_function | measured | bound | mnist | 0.7180 | 5.9163… | 0f377c425c6c… |
| primitive.credit_assignment.surrogate | measured | bound | mnist | 0.9030 | 7.9360… | a1298ce6dcbd… |
| primitive.credit_assignment.target_inversion | measured | bound | mnist | 0.1032 | 6.9725… | 79fa2e09da70… |
| primitive.credit_assignment.temporal_trace | measured | inert | mnist | 0.0968 | 9.7893… | bb0a9d77c613… |
| primitive.credit_assignment.thermodynamic_contrast | measured | bound | mnist | 0.7056 | 13.243… | 809f9d6b7cf3… |
| primitive.credit_assignment.unbiased_rtrl | refused | — | mnist | — | — | — |
| primitive.credit_assignment.zeroth_order | measured | bound | mnist | 0.1444 | 14.514… | dd84c79a1de1… |
| primitive.state_dynamics.diffusion | measured | bound | mnist | 0.1069 | 76.910… | ed1566af3286… |
| primitive.state_dynamics.energy_minimization | measured | bound | mnist | 0.8709 | 20.431… | b74c7d122abd… |
| primitive.state_dynamics.error_predictive_coding | measured | bound | mnist | 0.0982 | 21.109… | 17628dc08251… |
| primitive.state_dynamics.instantaneous | measured | inert | mnist | 0.8943 | 7.4939… | 84453097d227… |
| primitive.state_dynamics.lazy | measured | bound | mnist | 0.8705 | 47.220… | 6a10a6d37495… |
| primitive.state_dynamics.pc_alm | measured | bound | mnist | 0.5319 | 48.321… | a9c7fa2a1c0d… |
| primitive.state_dynamics.predictive_settling | measured | bound | mnist | 0.7096 | 26.456… | 5a59f8347fa4… |
| primitive.state_dynamics.spike_integration | refused | — | mnist | — | — | — |
| primitive.geometry.attention | measured | bound | mnist | 0.9113 | 17.710… | c76d95cc67a4… |
| primitive.geometry.causal_transformer | refused | — | mnist | — | — | — |
| primitive.geometry.conv | refused | — | mnist | — | — | — |
| primitive.geometry.feedforward | measured | bound | mnist | 0.4961 | 6.9692… | 053606687fb0… |
| primitive.geometry.graph | refused | — | mnist | — | — | — |
| primitive.geometry.nca | defective | bound | mnist | — | — | — |
| primitive.geometry.ntm | refused | — | mnist | — | — | — |
| primitive.geometry.recurrent | refused | — | mnist | — | — | — |
| primitive.geometry.routing | measured | bound | mnist | 0.2864 | 20.595… | 6c09ac80ac46… |
| primitive.geometry.spatial_lattice | measured | bound | mnist | 0.9050 | 19.034… | e7dddfa87218… |
| primitive.geometry.tile | refused | — | mnist | — | — | — |
| primitive.geometry.tile_mesh | measured | bound | mnist | 0.8453 | 33.472… | 2d5bc9967259… |
| primitive.plasticity.closed_form_ridge | measured | bound | mnist | 0.8872 | 5.0114… | a91f48c3a19c… |
| primitive.plasticity.conflict_adaptive | refused | — | mnist | — | — | — |
| primitive.plasticity.fast_weights | refused | — | mnist | — | — | — |
| primitive.plasticity.null | measured | inert | mnist | 0.8844 | 4.8425… | 84453097d227… |
| primitive.plasticity.routing | measured | bound | mnist | 0.8617 | 5.2763… | 56b5e91d0bdd… |
| primitive.plasticity.rule_state | refused | — | — | — | — | — |
| primitive.plasticity.substrate_coupled | refused | — | — | — | — | — |
| primitive.plasticity.temporal_psi | refused | — | mnist | — | — | — |
| primitive.substrate.analog | refused | — | mnist | — | — | — |
| primitive.substrate.complex | refused | — | mnist | — | — | — |
| primitive.substrate.digital | measured | inert | mnist | 0.8844 | 4.4678… | e579de77ba59… |
| primitive.substrate.memristive | refused | — | mnist | — | — | — |
| primitive.substrate.neuromorphic | refused | — | mnist | — | — | — |
| primitive.substrate.noisy | measured | inert | mnist | 0.8844 | 4.5724… | 634db2153fe9… |
| primitive.substrate.optical | refused | — | mnist | — | — | — |
| primitive.substrate.quantum | refused | — | mnist | — | — | — |
| primitive.substrate.sparse | measured | inert | mnist | 0.8831 | 21.300… | ecdd4cc27099… |
| primitive.substrate.ternary | measured | inert | mnist | 0.8624 | 10.198… | c98f30b22fd0… |
| primitive.parameter_update.adafactor | measured | bound | mnist | 0.9349 | 5.2509… | 69922631eb38… |
| primitive.parameter_update.adam | measured | bound | mnist | 0.9092 | 6.3196… | fd3d63cd766e… |
| primitive.parameter_update.bayesian_online | refused | — | mnist | — | — | — |
| primitive.parameter_update.cascade_synapse | refused | — | mnist | — | — | — |
| primitive.parameter_update.elastic_consolidation | refused | — | mnist | — | — | — |
| primitive.parameter_update.euclidean | measured | bound | mnist | 0.8844 | 4.6130… | d4e92e51272a… |
| primitive.parameter_update.lion | measured | bound | mnist | 0.9174 | 4.8707… | d902a5a37961… |
| primitive.parameter_update.local_adam | measured | bound | mnist | 0.7939 | 4.8206… | 4f0dd35abd73… |
| primitive.parameter_update.mean_norm | measured | bound | mnist | 0.9224 | 4.4665… | d7f27f99aa37… |
| primitive.parameter_update.muon | measured | bound | mnist | 0.9504 | 9.4041… | 1dead35be0f0… |
| primitive.parameter_update.natural_gradient | refused | — | mnist | — | — | — |
| primitive.parameter_update.ortho_adam | measured | bound | mnist | 0.9508 | 9.0547… | 78561e85ad89… |
| primitive.parameter_update.quantized_adam | measured | bound | mnist | 0.1899 | 5.4141… | eb6011f141a7… |
| primitive.parameter_update.riemannian_orthogonal | measured | bound | mnist | 0.9504 | 8.9138… | 7d3fe2f53394… |
| primitive.parameter_update.role_split | measured | bound | mnist | 0.9050 | 4.5752… | 28feb6f57f46… |
| primitive.parameter_update.schedule_free | measured | bound | mnist | 0.9167 | 4.7214… | 5ff357a2b8da… |
| primitive.parameter_update.spectral_constrained | measured | bound | mnist | 0.5755 | 16.841… | 6043ca2af856… |
| primitive.parameter_update.synaptic_intelligence | refused | — | mnist | — | — | — |

### Defects (execution facts, with their mechanism)
- `primitive.geometry.nca` — Training failed: NcaGeometry: flattened input has 784 features, but grid requires 768 (C=3, H=16, W=16)

### Refused (rule and reopen trigger)
- `primitive.credit_assignment.eligibility_prop` — `primitive.credit_assignment.eligibility_prop` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.credit_assignment.rtrl_reference` — `primitive.credit_assignment.rtrl_reference` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.credit_assignment.unbiased_rtrl` — `primitive.credit_assignment.unbiased_rtrl` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.state_dynamics.spike_integration` — `primitive.state_dynamics.spike_integration` composes no vision task family (declares neuromorphic, rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.causal_transformer` — `primitive.geometry.causal_transformer` composes no vision task family (declares lm, rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.conv` — cost cap: 60s after 1/24 boxes; last error: run deadline expired before the first epoch completed
- `primitive.geometry.graph` — `primitive.geometry.graph` composes no vision task family (declares graph); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.ntm` — `primitive.geometry.ntm` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.recurrent` — `primitive.geometry.recurrent` composes no vision task family (declares rl, sequence); the slice refuses it before it is priced (TODO95 S2)
- `primitive.geometry.tile` — cost cap: 60s after 1/24 boxes; last error: run deadline expired before the first epoch completed
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
