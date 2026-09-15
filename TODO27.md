# TODO27 — AutoScientist completion + Digital-substrate ontology atlas, wired into CEEC

Predecessors: TODO26b/c/d ran hand-built engine checks and produced
verdicts. This plan deliberately **does not initialize from those
results**. They are quarantined as validation anchors only (see §0.3) —
the exploration below re-derives whatever structure exists from a
standing start, because a discovery program seeded with its operators'
conclusions is just those conclusions, re-measured.

Scope lock: **Digital substrate** (`SubstrateType.DIGITAL`) only, until
§Phase 4 explicitly reopens the substrate axis. Every other axis — 7
dynamics, 9 credit families, ~13 update rules, 10 topologies, depth,
init — is in play.

## 0. Standing inventory (components, not conclusions)

### 0.1 The space
- **Dynamics (7):** energy_minimization, predictive_settling,
  error_predictive_coding, spike_integration, instantaneous, diffusion,
  lazy (`DYNAMICS_REGISTRY`).
- **Credit (9):** thermodynamic_contrast, local_contrastive,
  random_projections, local_goodness, temporal_trace, target_inversion,
  homeostatic, pepita, gradient (`CreditAssignmentConfig` factories).
- **Updates (~13):** euclidean, adam, local_adam, muon, unit_rms,
  mean_norm, spectral_constrained, ortho_adam, lion, role_split,
  elastic_consolidation, …
- **Topologies (10):** feedforward, recurrent, spatial_lattice, nca,
  ntm, causal_transformer, attention, conv, graph, tile_mesh
  (`GeometryConfig.topology_type`); init `default`/`mupc`; residual flag.
- **Tasks:** vision (mnist, fashion, cifar10/100, kmnist, svhn, usps,
  digits), tabular (iris, wine, breast_cancer, california_housing,
  circles, spiral), graph (cora, citeseer, pubmed), RL (cartpole,
  acrobot, pendulum), sequence/LM (char_ngram, tiny_shakespeare —
  executor currently incompatible; Phase 1 owns fencing), synthetic
  switching tasks (sign-of-mean / last-symbol, the harness the joint
  experiments ship).
- **Analysis stack already in the KB:** `train_surrogate`,
  `predict_outcome`, `compute_algorithm_fingerprints`,
  `map_failure_manifold`, `generate_algorithm_phylogeny`;
  `artifacts/permutation_coverage.json` (320 implemented / 144 tested /
  0 passing) is the scoreboard to move.

### 0.2 The machinery (defect state, fixed round 3c)
Campaign loop runs (persistence, insights, proposal → execution →
failure containment; vision trials execute). Remaining known defects
carried as work items: geometry/substrate-blind proposal schema,
2-rule hypothesis engine, broken LM loader (fence or fix), legacy
pyright on the files Phase 1 touches.

### 0.3 Quarantine rule (assumption hygiene)
Findings from TODO26b–d (co-design response, stability bands, trapped
channel, ψ ceiling, MNIST non-replication) are stored as KB entries
tagged `prior_operator_finding`. They may *seed the surrogate* and serve
as replication targets, but:
- the proposal ranking must not hard-code them (no preset tables built
  from this program's conclusions — the grid re-measures);
- any cell the atlas contradicts becomes a replication result either
  way, recorded in CEEC with both readings cited;
- no CEEC belief in this program cites a prior-operator finding as its
  only evidence.

## 1. Principles (unchanged by the clean-room stance)
1. **Instruments over narratives** — settle/credit tracing, split-half
   SNR, readout ceilings, attenuation profiles. A number without an
   instrument is an anecdote.
2. **Ruler calibration precedes every verdict.** No accuracy claim on a
   task whose BP ceiling at the same budget is unknown. Phase 0 builds
   this, it is not assumed from anywhere.
3. **Fail loudly, never fabricate.** Zeros stay zeros; executor-
   incompatible proposals fail with reasons.
4. **Predict → measure → reconcile.** Surrogates predict, the grid
   measures, the delta is itself data (surrogate reliability curve).
5. **Probe → gate → campaign escalation.** Engine tier free; CEEC
   governance begins where compute becomes real; never limbo.

## 2. Phases

### Phase 0 — Ground truth (no priors allowed)
- **P0.1 Ruler calibration:** BP sweep over the task catalog at the
  standard budget (quick-mode batch caps) — for each task, record
  BP-reachable accuracy and chance band. Output: the *ruler table*.
  Only BP-beats-chance tasks are campaign-eligible. Expect: vision and
  tabular pass; parity-class tasks fail; sequence tasks unresolved
  until the LM lane is fixed.
- **P0.2 Instrument calibration:** credit-trace (per-layer credit
  norm + split-half cosine) and settle-horizon instruments validated on
  systems with *known* properties (backprop credit on shallow nets —
  the instrument must read ≈BP's own gradient; a self-check, not a
  prior).
- **P0.3 Budget protocol:** one cell = one fixed budget (batches,
  epochs, lr at each family's own sweep — decided per family by a
  micro-sweep, not carried over from anywhere).
- *Acceptance:* ruler table committed; every instrument passes its
  self-check; a NaN/failure path is exercised once on purpose.

### Phase 1 — AutoScientist completion
- **P1.1 Geometry/topology/depth in the proposal schema and executor**
  (`ExperimentProposal.geometry`, pass-through in
  `Bridge.proposal_to_task` and `Campaign._execute_proposal`; native
  factories accept these kwargs, unknown keys fail loudly). Topology
  reach: tile/attention/recurrent/lattice/ntm/nca factories wired to
  the schema.
- **P1.2 Hypothesis generators, assumption-free:** (a) coverage-driven
  (propose untested `dynamics × credit × update × topology` cells,
  novelty read from the coverage matrix, pruned by
  `conditional_query`); (b) surrogate-guided ranking via
  `train_surrogate`/`predict_outcome` with in-flight calibration (the
  surrogate's reliability curve is itself an output); (c) instrument-
  triggered (a cell whose instrument shows a signature — e.g. zero-
  norm input credit — proposes the targeted follow-up cell that
  discriminates the hypothesis, not a blind neighbor).
- **P1.3 LLM backend, gated and optional** (`local_llm.py` behind
  config; output = proposals only, each pre-registered before
  execution; clean degrade to rules when absent).
- **P1.4 LM lane:** fence (dry-run compatibility gate) or fix (sequence
  batches the SystemTrainer consumes). Either way: no proposal may
  silently target an unrunnable task.
- *Acceptance:* a fresh KB (no prior-operator seeding beyond quarantine
  tags) yields ≥5 coverage-novel proposals across ≥3 axes; a geometry
  proposal executes and is reproducible bit-for-bit; surrogate
  reliability logged from iteration 1.

### Phase 2 — CEEC integration
- **P2.1 Proposal = pre-registration.** `record_probe_result` writes
  prediction + threshold + scope before execution; `ingest_verdict`
  + calibration record after. Never limbo.
- **P2.2 Belief updates:** green strengthens; red at lever exhaustion
  routes to `gates.evaluate_boundary`. Single-seed iterations stay
  Level 4/5 — promotion requires the full gate set.
- **P2.3 Approval gate on real compute:** `human_approval_gate=True`
  for multi-seed/real-task spends; gate decisions in the ledger.
- **P2.4 Shared record format:** governed rounds run through
  `computronium_lab.Lab` + `ProbeResult` + ledger SQLite (the H24.3
  harness pattern) so AutoScientist and CEEC speak one format.
- *Acceptance:* one trace: proposal → pre-registration → execution →
  verdict → calibrated gate result, audit-clean.

### Phase 3 — The blind grid (the discovery campaign)
Executed by the AutoScientist, certified by CEEC, digital substrate
only:
- **G1. Core sweep:** dynamics × credit × update on feedforward,
  depth {2, 8, 20}, 2 geometry inits (`default`, `mupc`), ruler-table
  tasks only, standard budget, seeds per gate tier. The proposer ranks;
  the executor runs; the KB records; surrogates retrain each iteration.
- **G2. Topology extension:** surviving cells re-run across
  {recurrent, spatial_lattice, nca, ntm, tile} — where does any
  structure found in G1 survive a topology change?
- **G3. Instrument-first triage:** failing cells get the instrument
  battery (credit trace, settle horizon) before more training budget —
  the campaign diagnoses before it retries.
- **G4. Convergence analysis:** `compute_algorithm_fingerprints` +
  `map_failure_manifold` + `generate_algorithm_phylogeny` over the
  results; coverage matrix regenerated. The atlas — families, their
  working geometries, their failure signatures — is the deliverable.
- *Stop rules:* campaign proposing only tested cells → P1.2 reopens;
  surrogate below chance+ε for 2 iterations → declared uninformative
  (boundary record); any verdict without ruler calibration → halt.

### Phase 4 — Certification & the first expansion (only after G1–G4)
- **C-cert:** the atlas's strongest structure (a training family, a
  rescue/refusal pattern, or a boundary) runs the full CEEC gate set
  (multi-seed, matched control, defect hunt, audit) — first certified
  AutoScientist-origin record, promotion or boundary.
- **Substrate unlock (deferred by scope lock):** re-run the atlas's
  surviving cells under `ANALOG`/`MEMRISTIVE` specs. *This is where the
  substrate thesis gets its first real test — deliberately sequenced
  after the digital map exists, so any substrate divergence has a
  digital baseline to be measured against.*
- **Z3 gate:** any P-axis claim resumes only through the frozen-θ
  harness with an instrument reading against the ruler.

## 3. What counts as a breakthrough here
A structure the operators did not put in: a family-response law
re-derived by the campaign from cells chosen without that prior; a
surrogate that predicts the grid; an instrument signature that predicts
trainability before training; a certified boundary with mechanism. The
atlas itself — measured, coverage-complete, audit-clean — is the
deliverable regardless of which structures appear.

## 4. Hygiene riders
- `autoscientist/campaign.py` + `proposer.py` legacy pyright (lines
  262/585/604/800/824; 178/217) ride the Phase-1 edits.
- `ontology/geometry.py` LSP strictness rides P1.1's topology work.
- LM loader defect is P1.4's; fix or fence, decided by P0.1's ruler
  table (a fenced lane is acceptable if sequence tasks never enter the
  campaign).