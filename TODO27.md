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

## 5. Progress log (rev 4 — Phase 1 complete)

### Rev 2 (engine round)
- **P1.1 complete.** New `computronium/autoscientist/compose.py` is the
  single composition path for proposals:
  - `ExperimentProposal.geometry` (topology/depth/hidden_dim/init_scheme/
    init_scale + topology extras) added; `Bridge.proposal_to_task` and
    `Campaign._execute_proposal` pass it through. Unknown or
    topology-inappropriate geometry keys raise `ProposalComposeError`
    (fail loudly).
  - `compose_proposal_system` resolves a geometry override by
    round-tripping the base native factory through
    `extract_config`/`compose_system_from_configs` — proposal and trainer
    cannot diverge on construction. Verified end-to-end: a geometry
    proposal (recurrent/mupc on digits) executes via `SystemTrainer`.
  - `compose_cell_system` composes a full G1 cell
    (dynamics × credit × update × topology) from the single-source config
    classmethods — no preset tables (quarantine rule respected).
  - `build_geometry_config` reaches all of feedforward/recurrent/
    tile_mesh/attention/spatial_lattice/nca/ntm/conv/graph.
- **P1.2(a) complete.** `ExperimentProposer.propose_coverage_cells`:
  novelty read from the KB's own experiment records (cell key =
  `dynamics|credit|update|topology`), product-ordered over the registries
  (no ranking priors), pruned by `conditional_query` via
  `avoid_characterized`. P1.2(b) surrogate-guided ranking and P1.2(c)
  instrument-triggered follow-ups remain.
- **P1.4 complete (fence variant).** `assert_task_runnable` fences
  char_ngram/shakespeare/wikitext2/penn_treebank with reasons and rejects
  unknown task names (closing the domain factory's silent LM fallback at
  the proposal layer). The executor path cannot spend budget on a fenced
  task. The fix variant (sequence batches for SystemTrainer) stays open
  and is only worth doing if sequence tasks enter the campaign.
- **P0.1 instrument built, partial table.**
  `scripts/probes/ruler_calibration.py` measures the BP ceiling +
  chance band per task at the standard budget and writes
  `artifacts/ruler_table.json`. First (small) table: digits 0.189 @
  3-epoch quick budget (eligible), iris 1.0 (eligible), spiral at
  chance (ineligible — parity-class, as predicted). Full-catalog sweep
  is a background job, not yet run.
- **Riders cleared.** campaign.py/proposer.py flagged pyright lines and
  geometry.py LSP strictness (5 errors) now report 0. Ruff 0.15
  directive conversion applied across `autoscientist/`.
- **Tests:** `tests/unit/test_autoscientist_compose.py` (17 cases:
  override composition, loud failures, LM fence, coverage novelty/dedup,
  bridge pass-through) + existing `test_campaign_stack.py` — 56 passed.

### Done in rev 4 (CEEC + surrogate round)
- **P2.1/P2.4 complete.** New `computronium/autoscientist/ceec_link.py`:
  `CEECLink` wraps a `ceec.session.Session` ledger. One trace per
  governed proposal — `pre_register` (question/prediction/threshold via
  `falsification_criterion`/scope with the resolved cell key, design
  carries geometry + all grid axes) -> execute -> `ProbeResult` ->
  `Session.record_result` (decision, artifact, vector evidence,
  calibration, gate evaluation). Failures land as a `failed` experiment
  status plus a `missing` probe-output evidence — never limbo. The
  campaign runs governed whenever `ceec_ledger_path` is passed
  (`AutoScientistCampaign(..., ceec_ledger_path=...)`); ungoverned runs
  are unchanged. Verified end-to-end including the failure path.
- **P1.2(b) complete.** `train_surrogate` now featurizes the grid axes
  (`dynamics`/`credit`/`update`/`topology` one-hot via `get_dummies`)
  and `predict_outcome` makes real predictions from the in-process
  fitted model (`_LIVE_SURROGATES`; no-model fallback reports the stored
  R2 floor, never a fabricated number). The campaign writes every result
  to the experiments table via `kb.add_experiment` with the full axes in
  config, so surrogate and coverage matrix read one record format
  (shared with the CEEC artifact payload). Verified: prediction on an
  unseen cell returns a real value; covered cells are no longer
  re-proposed.
- **P1.2(c) complete.** `ExperimentProposer.propose_instrument_triggered`:
  reads a `credit_trace` reading and proposes the *discriminating*
  follow-up — zero input-layer credit -> same cell at depth+8 with muPC
  init; unreliable split-half cosine -> doubled-batch reliability
  recheck. Quiet readings propose nothing.
- **Phase 1 acceptance status:** coverage-novel proposals across >=3
  axes (dynamics/credit/update/topology) done; geometry proposal
  executes and composes through one round-trip path done (bit-for-bit
  reproducibility still needs an explicit seeded double-run test);
  surrogate reliability logging during G1 ranking is the remaining
  wiring.

### Improvement opportunities (rev 4)
1. **Family-geometry compatibility is unmeasured**: pepita x recurrent
   crashes with a shape mismatch at settle time. The fence catches task
   incompatibility, but credit x topology crashes cost a failed ledger
   row each. A static compatibility table (or a dry-run constructor
   probe before pre-registration) would save governed budget —
   candidate for the G1 dry-run gate.
2. **Reproducibility test**: P1.1 acceptance asks for bit-for-bit
   reproducible geometry execution; needs an explicit seeded double-run
   test before G1.
3. **`predict_outcome` model persistence**: live models are process-
   local; a restart drops them (registry rows persist). Pickle to
   `model_path` if G1 needs cross-process ranking.
- **Surrogate features are hyperparameters-only** — RESOLVED in rev 4
  (grid-axis featurization; campaign records the axes).

### Done in rev 3 (instrument round)
- **P0.2 complete.** New `computronium/analysis/instruments.py`:
  - `credit_trace`: per-weight-layer credit norm, split-half cosine
    reliability, and an optional BP-reference cosine computed against a
    plain routed-forward autograd gradient of the same batch.
  - `settle_horizon`: settle steps actually consumed (None when the
    dynamics does not expose a free-energy history — recorded as an
    instrument gap, not fabricated).
  - Self-check PASSED: GradientCredit reads BP's own gradient at
    cos 0.9998 ≥ gate 0.9 (`BP_COSINE_GATE`). ThermodynamicContrast
    reports a depth-attenuating alignment profile (0.574 → 0.242 →
    0.163 across layers 1/2/3) — an instrument reading consistent with
    the quarantined attenuation finding, here re-derived, not assumed.
  - Probe: `scripts/probes/instrument_selfcheck.py` (asserts the gate;
    recorded-measurement script per the probe conventions).
- **P0.3 NaN-path exercised once, on purpose.** A NaN input batch
  surfaces as NaN in every credit norm — the failure is loud, never
  zero-filled (asserted in the self-check probe).
- **Improvement 1 landed.** `domains/factory.create_task` no longer
  silently defaults unknown task names to the LM lane — it raises with
  the registry pointer. The proposal-layer fence
  (`assert_task_runnable`) remains as belt-and-suspenders.
- **Improvement 3 landed (trap removed).** `GeometryConfig` now carries
  `neurons_per_tile`/`tiles_per_layer`; `geometry_from_config` dispatch
  uses them (was hardcoded 8/2 — the G2 round-trip would have silently
  rebuilt every tile system at the wrong dims). `core/presets.py` tile
  preset stores the values too.
- **Full-catalog ruler sweep complete (rev 3).** The final table
  (`artifacts/ruler_table.json`) sweeps the offline-resolvable
  vision+tabular catalog with the lr micro-sweep; all 11 tasks eligible.
  First-pass defect caught by skepticism rider: the fixed-lr ruler
  under-measured digits at 0.189 (true ceiling 0.831 at lr 1e-2) —
  exactly the mismeasure that would have corrupted G1 eligibility
  verdicts.

### Improvement opportunities from rev 2 (status)
1. **Route `domains/factory.create_task` through
   `domains/registry.resolve_task`** — DONE in rev 3 (loud-raise
   variant: unknown names now raise with the registry pointer).
2. **`geometry_from_config` tile dispatch hardcodes
   `neurons_per_tile=8, tiles_per_layer=2`** — DONE in rev 3 (config
   now carries tile dims; dispatch and presets use them).
3. **No `muon` classmethod on `ParameterUpdateConfig`** — DONE in rev 3
   (exact-polar alias; `GRID_UPDATES` covers the full axis).
4. **digits BP ceiling 0.189 at the quick budget is suspiciously low**
   — RESOLVED in rev 3: root cause was the fixed lr (1e-3 under-trains
   the small offline datasets at the 3-epoch budget). The ruler now
   micro-sweeps lr {1e-3, 1e-2} per task (P0.3's own rule) and the
   re-measured table reads digits 0.831, mnist 0.971, fashion 0.858,
   kmnist 0.862, usps 0.891, xor 1.0, spiral 0.955, circles 1.0,
   iris/wine/breast_cancer 0.97+ — every offline catalog task eligible.
5. **Surrogate features are hyperparameters-only** (`train_surrogate`
   reads lr/batch_size/hidden_dim/num_layers/epochs); G1 cells need
   dynamics/credit/update/topology features or the surrogate cannot
   learn the atlas (P1.2b dependency) — DONE in rev 4 (featurization +
   campaign experiments-table rows).

### Changes that clarify remaining work
- The proposal → executor contract is now "compose through
  `compose.py` or don't execute" — Phase 2's pre-registration record can
  cite the resolved cell key directly.
- Campaign eligibility is now mechanically checkable from
  `ruler_table.json` (`eligible: true` + `TASK_COMPAT`), so the G1 stop
  rule "any verdict without ruler calibration → halt" has a concrete
  artifact to halt on.
- Phase 0 acceptance: **COMPLETE as of rev 3** — ruler table committed
  (`artifacts/ruler_table.json`, micro-swept lr), instrument self-check
  passed (BP cos 0.9998 ≥ 0.9), NaN/failure path exercised (surfaces
  loud). Next implementation front: **Phase 2 (CEEC pre-registration
  format)**; P1.2b/c and the G1 sweep can start from the committed
  ruler.
- New gap found by the sweep: `SUPPORTED_TASKS` lists
  `diabetes`/`california_housing` but `create_task` has no resolution
  path for them (now fails loudly instead of silently hitting the LM
  lane) — add the tabular cases or drop them from the registry before
  the catalog claims them.
## 6. Fresh-session entry point
State at rev 4: Phase 0 acceptance-complete, Phase 1 complete,
P2.1/P2.4 landed (commit 13c63790). Next actions in order:
1. Reproducibility acceptance: seeded double-run test of a geometry
   proposal through `_execute_proposal` (bit-for-bit history).
2. Dry-run constructor probe before `CEECLink.pre_register` — catches
   credit×topology crashes (pepita×recurrent is a known bad pair)
   without burning a governed ledger row.
3. G1 core sweep as a background campaign: fresh KB, ruler-eligible
   tasks only, `ceec_ledger_path` set, `propose_coverage_cells` +
   `train_surrogate` each iteration. Stop rules in §3/G1.
4. After G1: G2 topology extension (tile dims now round-trip), G4
   fingerprint/phylogeny analysis.
Watch: `git log` for this file's rev headers; `uv run python -m pytest
tests/unit/test_autoscientist_compose.py tests/unit/test_ceec_link.py
tests/unit/core/test_campaign_stack.py -q` is the smoke gate.
