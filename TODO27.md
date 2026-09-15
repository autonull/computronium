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

## 5. Progress log

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
### Rev 11 (credibility round: BP-leakage audit + matched-budget BP control)

Operator asked the right questions: are we comparing to BP; do we trust
the results; do they indicate bugs. Two instruments added:

- **`scripts/probes/credit_channel_audit.py`**
  (`artifacts/credit_channel_audit.json`): BP-cosine of the credit
  signal for all four measured family|credit pairs. **No leakage** —
  every cosine is far below the 0.9 GradientCredit gate. The pattern is
  itself a finding: em|tc's credit is substantially gradient-aligned
  (0.44-0.60 across layers, consistent with the rev-3 attenuation
  profile) while ps|tc is near-orthogonal (0.0-0.23). So
  predictive_settling beating em is NOT ps secretly doing backprop.
- **Matched-budget BP control arm**: `ruler_calibration.py --epochs 1`
  now sweeps epoch budgets; `artifacts/bp_control_ep1.json` holds the
  1-epoch BP control on the catalog. Verdict vs the 1-epoch ps cells:
  **ps beats matched-budget BP on digits (+0.53), spiral (+0.16),
  circles (+0.09)**; parity on wine/breast_cancer; loses on xor/usps/
  iris. A local method beating same-budget BP per epoch is a
  plausible local-learning result (per-epoch sample efficiency), but a
  +0.53 gap is large enough that the verdict is **provisional until
  multi-seed replication** (the C-cert gate set: seeds, matched
  control at multiple budgets, defect hunt).
- Resolved: the campaign log's "mean accuracy 0.000" insight is the
  reasoner averaging confidence over the 50 confidence-0.0
  `structurally_incompatible` entries — read-path artifact, not a
  measurement bug; the reasoner should exclude them.
- Tests: compose suite green; ruff clean on all touched probe scripts.

### Rev 10 (shallow breadth run: predictive_settling measured, first cross-family signal)

- **Protocol change honored:** `--epochs N` / `--skip-dynamics` /
  `--cells-per-iter` rapid-breadth run (1-epoch cells) measured 84
  predictive_settling task-cells in ~25 min (was: 51 em cells in ~2.5 h
  at 5 epochs). 193 task-cells / 92 distinct coordinates / 207
  structural rejections recorded total. Sweep stopped at its kill
  deadline, 0 stray processes.
- **First cross-family signal:** predictive_settling *out-measures*
  energy_minimization on the same grid (mean 0.545 vs 0.508) with a
  much lower vision failure rate (7/29 vs 15/26 below 0.3) — the
  em-slice vision weakness is looking family-specific, not a general
  local-learning limit.
- **ps axis readings (n>=6):** credit tc 0.566 > local_contrastive
  0.487 (credit ranking FLIPS vs em — the atlas's first family x credit
  interaction); update lion 0.732 > ortho_adam 0.713 > local_adam;
  topology ff 0.579 ~ recurrent 0.557 > tile 0.462.
- **Still unreachable:** attention/spatial_lattice/ntm/nca/graph for
  both families so far (layered-geometry requirement). Error_predictive_
  coding / spike_integration / diffusion / lazy remain unmeasured —
  next shallow run should skip em + predictive_settling.
- Tests: compose suite green; ruff/pyright clean on touched files.

### Rev 9 (decision snapshot at 109 cells + shallow-run protocol)

- **Sweep run 3 stopped by operator at 109 measured task-cells
  (51 distinct coordinates), 132 structural rejections recorded, 0
  stray processes.** Still all `energy_minimization` — the em slice's
  product-order region is dominated by structurally impossible
  coordinates (em x attention 55, em x spatial_lattice 54 recorded
  rejections), which the coverage driver burns gate probes on before
  reaching composable cells. The `avoid_characterized` task-level
  prune was removed from `propose_coverage_cells` (it had killed all
  novel proposals once any task exceeded 0.5 — cell novelty is the cell
  key, not the task).
- **Decision-relevant readings (5-epoch cells, n>=6):**
  - credit: local_contrastive 0.528 >= random_projections 0.520 >
    thermodynamic_contrast 0.499 — tc is the most-used but
    weakest-measuring credit so far.
  - update: adam 0.597 > ortho_adam 0.562 > euclidean 0.560 >
    local_adam 0.529.
  - topology: feedforward 0.534 ~ tile_mesh 0.531 > recurrent 0.469.
  - 15/26 vision cells read < 0.3 while their BP ruler is 0.83-0.97:
    either genuine family limits or under-training at the cell budget
    (per-topology ruler calibration is the discriminating instrument).
  - Structural map: em composes with {ff, recurrent, tile_mesh};
    attention/spatial_lattice/ntm/nca/graph are em-blocked (layered
    geometry). These axes need the OTHER dynamics families to matter.
- **Shallow-run protocol (operator directive):** future sweeps default
  to rapid shallow breadth. `--epochs N` on `scripts/g1_core_sweep.py`
  (default 5) stamps epochs into every coverage proposal;
  `_execute_proposal` honors `hyperparams["epochs"]`. Run
  `--epochs 1 --cells-per-iter 8` for many datapoints suitable for
  high-dimensional analysis; reserve 5-epoch runs for confirmatory
  depth on survivors.
- Tests: compose suite 18/18; ruff/pyright clean on touched files.

### Rev 8 (G4 analysis + two KB-write defects fixed + live surrogate)

- **Defect: experiments-table rows collided within an iteration.**
  `experiment_id`/`name` were `campaign_iter{N}` for every result, so 51
  executions produced 18 rows — all but one cell per iteration was
  silently lost to the surrogate's read path. Fixed: cell-unique
  identity (`campaign_iter{N}_{cell_key}`).
- **Defect: surrogate target metric never matched.** The executor
  records `final_accuracy`; `train_surrogate` targets `val_accuracy` —
  the surrogate had zero valid records (rev-4 featurization was dead
  code in practice). Fixed: both names recorded. KB repaired by
  backfilling the 51 measured results from the authoritative
  `surrogate_reliability.jsonl` (same measured values, honest alias)
  and aliasing `val_accuracy` on existing rows.
- **Surrogate is now live:** trained (rf) on 69 experiment rows; real
  predictions on covered (em|tc|eucl|recurrent -> 0.533) and unseen
  (ps|pepita|lion|attention -> 0.35) cells. No-model floor only until
  the first fit.
- **`artifacts/g1/atlas.md` written (G4 partial):** top-15 cells, mean
  accuracy by credit/update/topology axis (local_contrastive 0.538 vs
  thermodynamic_contrast 0.491; local_adam best update), failure
  manifolds by dynamics x topology pair, G2 topology-survival preview,
  surrogate reliability summary. The KB's `compute_algorithm_fingerprints`
  / `generate_algorithm_phylogeny` return empty for this data (they key
  on model_family diversity — all cells are eqprop) — the atlas is
  computed from the grid axes instead.
- **Tests:** reproducibility suite 8/8 (bit-for-bit excluded from the
  quick loop only when re-running cheap tiers), pyright 0/ruff clean on
  campaign.py (3 pre-existing findings remain: Register C).

### Rev 7 (G1 run 2 complete — first measured atlas slice)

Sweep run 2 (24 iterations x up to 6 cells, full ruler catalog) finished
inside its kill deadline, **0 stray processes**, ledger audit-clean:

- **Measured: 51 cells / 43 distinct coordinates** — all
  `energy_minimization` (registry product order is dynamics-outer, so the
  sweep covered the em slice: 9 credits x 12 updates x 10 topologies
  precedes any other family). Best cells: local_contrastive x adam on
  xor 1.000, thermodynamic_contrast x euclidean x recurrent on
  breast_cancer 0.956, tc x local_adam x ff on digits 0.911,
  tc x muon x ff on mnist 0.851.
- **Gated: 58 rejections, all recorded covered** — 24
  "requires a layered geometry" (em x attention/lattice/ntm), 3
  local_contrastive x non-linear-stack, and **8 role_split
  compositions that were an implementation defect, not structure**:
  `compose_cell_system` passed `step_size=` to a factory that doesn't
  take it. Fixed (signature-aware kwargs) — but the real finding is that
  `role_split` requires role metadata the grid does not parameterize, so
  it is **removed from `GRID_UPDATES`** and its 8 wrongly-attributed
  `structurally_incompatible` KB entries purged (wrong claims in the
  atlas are worse than missing ones).
- **Stop-rule behavior validated:** once cheap cells were exhausted the
  sweep advanced through gate-only iterations at ~0s each and terminated
  cleanly on the iteration cap — no limbo, no budget burn.
- **Reliability curve:** 51 predicted-vs-measured rows; the first ~10
  are the R2 floor (surrogate cold start), the tail reflects real fits.
  Curve analysis is a G4 input.
- **Tests:** compose suite (18) + reproducibility suite (8) + ceec_link —
  30 passed; ruff/pyright clean on touched files.

**G4 partial (to finish next):** the coverage matrix, fingerprints, and
phylogeny over `artifacts/g1/kb.sqlite` remain; the em-slice numbers
above are the seed of `artifacts/g1/atlas.md`.

### Rev 6 (G1 run-1 triage: three sweep defects fixed, sweep relaunched)

G1 sweep run 1 (rev 5, 12x4) hit the stop rule after 8 iterations with
only 8 governed cells measured and 18 dry-run rejections — triage found
three defects, all structural, all fixed:

1. **Coverage matrix never accumulated.** `_covered_cells` reads
   `hp["dynamics"]` from KnowledgeEntry records, but
   `_update_knowledge_base` never wrote `dynamics/credit/update` into
   the entry's hyperparameters — every visit re-proposed the same first
   product-order cells and the stop rule fired spuriously. Fixed: the
   entry now carries the full cell key.
2. **Gated cells were re-proposed forever.** A dry-run rejection left no
   record, so structurally impossible cells
   (`energy_minimization x attention/lattice/ntm` — "requires a layered
   geometry"; tile-mesh shape mismatches) burned the campaign in a loop.
   Fixed: `_dry_run_gate` now records the rejected cell as covered via a
   `structurally_incompatible` KnowledgeEntry (no `add_experiment` row —
   a zero-accuracy row would poison the surrogate). The gate remains
   ledger-free; the incompatibility verdict is data, measured not
   assumed.
3. **Cells under-trained at the fixed default lr.** G1 run-1 vision
   cells measured ~ chance (mnist 0.089 vs ruler 0.971) — the exact
   fixed-lr mismeasure the rev-3 ruler round caught. Fixed:
   `_ruler_lr(task, topology)` defaults a proposal's lr to the task's
   ruler-calibrated lr — **scoped to feedforward**, the topology the
   ruler actually measured (recurrent at the ruler's 1e-2 destabilizes:
   0.13 measured in triage; extrapolating a calibration instrument past
   its measured scope is fabrication, not calibration).

- **Tests:** `test_campaign_reproducibility.py` now 8 cases (added:
  incompatible cell enters the coverage matrix and stops re-proposal —
  verified against a real `energy_minimization x attention` rejection;
  ruler-lr scoping; explicit-lr precedence via the dry-run payload, which
  now reports the resolved `lr`). 8/8 + compose/ceec suites pass; ruff +
  pyright clean on touched files.
- **Sweep run 2 launched (rev 6):** 24 iterations x 6 cells, full
  ruler-eligible catalog, fresh `artifacts/g1`, seed 20260914. Iteration
  1 measured 3/4 (one gate rejection, now recorded). Kill deadline 3 h.
- **Reliability-curve caveat (carried):** `predict_outcome` returns the
  R2 floor (0.0) until ~10 experiment rows exist; run 1's reliability
  JSONL is all-floor. Meaningful curve starts mid-run-2.

### Rev 5 (acceptance + gate + G1 launch)

- **Reproducibility acceptance complete.**
  `tests/unit/test_campaign_reproducibility.py`:
  `test_geometry_execution_is_bit_for_bit_reproducible` double-runs a
  geometry proposal (recurrent/mupc on digits) through
  `_execute_proposal` with `seed_everything(1234, deterministic=True)` and
  asserts bit-for-bit identical training histories. P1.1 acceptance is now
  fully closed.
- **Improvement 2 landed (dry-run constructor gate).**
  `compose.dry_run_system` runs one synthetic `train_step` on the composed
  system;
  `AutoScientistCampaign._dry_run_gate` runs it *before*
  `CEECLink.pre_register` for governed campaigns — an incompatible cell is
  rejected with no ledger row (log carries the reason; `run_iteration`
  skips it). Note: pepita×recurrent no longer crashes at depth-2/hidden-16
  (the rev-3 round-trip path evidently fixed it); the gate remains the
  mechanism, the specific pair is no longer a known failure.
- **Surrogate reliability logging landed.** `_execute_proposal` now
  returns `dynamics`/`credit`/`update` in its result payload (they were
  missing — caught live by the reliability log recording `None` cells).
  `scripts/g1_core_sweep.py` appends predicted-vs-measured rows to
  `surrogate_reliability.jsonl` each iteration; the surrogate retrains
  per iteration (graceful skip below the minimum row count).
- **G1 core sweep launched (rev 5).** `scripts/g1_core_sweep.py`:
  fresh KB, ruler-eligible tasks from `artifacts/ruler_table.json`,
  CEEC-governed (`--root artifacts/g1`, ledger SQLite + campaign db +
  reliability JSONL under one root), coverage driver rotating tasks per
  visit, stop rule on no-novel-cells. First sweep: 12 iterations × 4
  cells, full catalog, seed 20260914. Kill deadline 3 h after launch.
- **Tests:** `tests/unit/test_campaign_reproducibility.py` (5 cases);
  smoke gate `test_autoscientist_compose + test_ceec_link +
  test_campaign_stack` 61 passed; ruff/pyright clean on all touched

### Improvement opportunities (rev 8)
1. **Continue the sweep for the other 6 dynamics families** — same KB,
   new campaign root; coverage skips completed/incompatible cells; the
   surrogate trains from ~iteration 2 now (target metric fixed).
2. **KB analysis stack keys on model_family, not grid axes** —
   `compute_algorithm_fingerprints`/`phylogeny` return empty for
   single-model campaigns; extend analyzers to the axis featurization
   or record axes as family variants (decision rides G4 completion).
3. **G3 instrument triage on divergence cells** (energy -> -1e19):
   classify instability vs trap with credit_trace/settle_horizon
   before G2 re-runs them on other topologies.
4. **Per-topology ruler calibration** before trusting G2 (ruler lr is
   feedforward-only by design).
5. **Surrogate persistence**: pickle to `model_path` for cross-process
   resume.
6. **role_split accessibility**: needs `update_params` in the proposal
   schema if the axis matters.

### Fresh-session entry point (rev 8)
1. Continue G1 (background, with kill deadline):
   `setsid nohup uv run python scripts/g1_core_sweep.py --iterations 24
   --cells-per-iter 6 --root artifacts/g1 >> logs/g1_sweep.log 2>&1 &`
   — same KB advances past the em slice into predictive_settling et al.
   Verify `experiments` rows grow per-cell (collision fixed).
2. Extend `artifacts/g1/atlas.md` after each run from
   `surrogate_reliability.jsonl` + the KB.
3. G2 topology extension once multiple dynamics families have measured
   survivors; G3 divergence triage first.
4. Phase 4 (C-cert, substrate unlock) only after G1-G4.
5. Smoke gate: `uv run python -m pytest
   tests/unit/test_autoscientist_compose.py
   tests/unit/test_campaign_reproducibility.py
   tests/unit/test_ceec_link.py -q`.

## 6. Fresh-session entry point
Superseded by the **rev 8** entry point above.

State at rev 8: Phases 0-2 complete, G1 run 2 measured the em slice
(51 cells, atlas written, surrogate live), two KB-write defects fixed.
Next front: sweep continuation -> G2/G4 -> Phase 4.
