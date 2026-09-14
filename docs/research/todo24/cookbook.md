# Mechanism Cookbook v1

Certified entries: 2 (1 promotion, 1 boundary); refusals: 0.

## backprop_mlp — flat_classification

Mechanism: backprop_mlp
Problem class: flat_classification
Constraints: digital, float32, cpu_quick
Coordinate: {'substrate': 'digital', 'geometry': 'mlp', 'dynamics': 'instantaneous', 'plasticity': 'null', 'credit': 'bp', 'update': 'euclid'}
Evidence: belief B-SYNTH-BACKPROP-MLP-002: campaigns [backprop_mlp@flat_classification/gaussian_blob/digital/float32/continual=False/local=False/dims=32x4]; controls {'flat_classification/gaussian_blob/digital/float32/continual=False/local=False/dims=32x4': 0.21875}
Certificates: promote_mechanism §18 gates; ledger-audited
Known limitations: saturates the quick tier by 10-20 epochs; sequence/parity unmeasured for this entry
Deployment notes: onnx export path verified by campaign DeployabilityCheck; int8/ternary transfer deltas in transfer report


## ntm_classifier — sequence_parity (certified negative result)

Mechanism: ntm_classifier
Problem class: sequence_parity
Constraints: digital, float32, cpu certified operating point (120 epochs x 3 seeds)
Coordinate: {'substrate': 'digital', 'geometry': 'ntm', 'dynamics': 'instantaneous', 'plasticity': 'null', 'credit': 'bp', 'update': 'euclid'} (BPTT through the unrolled episode)
Evidence: belief B-PARITY-CHANCE-001 (boundary): accuracies [0.4688, 0.5391, 0.5313], mean 0.5130, verdict abs(mean - 0.5) <= 2 SE(n=3); lr lever sweep 0.01/0.1/0.3 all within the chance band; defect hunt: task pipeline shared with last_symbol (0.918-0.922 @ 120ep recorded)
Certificates: CEEC-Core 19 boundary gates (rescue_probability_threshold, defect_hunt_passed, integrity_checks_passed, known_levers_exhausted, matched_control, multi_seed_where_feasible, scope_explicit) — all passed
Known limitations: per-seed accuracy at the 32-episode val split carries ~0.09 binomial SE, so only mechanism-class-level claims (not small deltas) are decidable at this budget; a capacity-matched recurrent architecture was not swept
Deployment notes: parity is not learnable by the current NTM construction at the recorded budget — do not deploy parity classifiers built from this path; reopening triggers (TODO23 R-series) apply if a new memory mechanism class appears
