> **STATUS: IMPLEMENTATION COMPLETE (2026-09-15); 50-cell pilot clean.**
> All four phases shipped and smoke-verified end-to-end. Three pre-run
> blockers resolved (anomaly = credit×update draw composition;
> instruments settle_horizon/σ_max(J)/credit_alignment captured per cell;
> topology lr confound fixed). Deferred defects fixed before experiments:
> diffusion now settles geometry Hopfield energy (was a prior-only walk),
> device-poisoning lazy-init class eliminated, sweep resume crash fixed.
> **Improvements addressed:** stratification now balances credit×update pairs
> (not just dynamics); multi-task atlas supports task facet (color by task,
> symbol by dynamics). Artifacts: `artifacts/broad_map_pilot50/` (52 cells,
> 0 failed; `atlas.html`), `docs/figures/d28_broad_atlas.png` (regenerated
> at n=82 measured cells).
>
> **EXECUTION READY:** The 500-cell production run is unblocked and
> can be launched with:
> ```bash
> nohup uv run comp gallery --generate-broad-demo --epochs 1 --sample-size 500 --credit-trace > logs/broad_map_500.log 2>&1 &
> ```
> Expected walltime: ~2-4 hours on GPU (dominated by settling families
> em/ps at max_steps). Use `--cells-per-iter 10` and 2-min poll cadence
> per AGENTS environment rules. The run now captures
> settle_horizon/σ_max(J)/lr/credit_alignment per cell — no re-run needed
> for instruments.

To achieve a **broad focus** with **useful preliminary results** and a **crystallizing high-dimensional visualization**, we need to temporarily pivot the AutoScientist from *intelligent search* to *stratified mapping*. 

The current sweep is trapped in the `energy_minimization` (em) slice due to the product-order bug and the broken surrogate model. To build a compelling visualization (like t-SNE/UMAP), you need data points from **all 7 dynamics families** and across the topological spectrum. A t-SNE of only `em` and `ps` will just show a single blob; a t-SNE of the whole space will reveal the "islands" of viable algorithms and the "voids" of structural incompatibility.

Here is the strategic execution plan to deliver this demonstration.

---

### Phase 1: The "Broad Map" Data Generation (Bypassing the Trap)
Do not waste time fixing the surrogate model or the coverage driver right now. Instead, write a **Stratified Random Sampler** that forces the execution of cells across the entire 6-D ontology. 

**The Script: `scripts/broad_mapping_sweep.py`**
1. **Stratify by Dynamics:** Ensure you pull an equal number of random configurations from all 7 dynamics families (`em`, `ps`, `error_predictive_coding`, `spike_integration`, `instantaneous`, `diffusion`, `lazy`).
2. **Use the Dry-Run Gate:** Since random sampling will generate thousands of structurally impossible combinations (e.g., `em` + `attention`), rely heavily on the `compose.dry_run_system` gate. 
   * *Crucial Epistemic Rule:* Do not log dry-run failures to the CEEC ledger as "experiments." Log them to a separate `structural_voids.jsonl` file. These voids are actually a massive scientific finding: they define the physical boundaries of the Computronium space.
3. **Shallow Budget:** Stick to the 1-epoch rapid protocol. You want 500–1,000 diverse data points, not 50 deeply trained ones.
4. **Record to CEEC:** Every cell that *passes* the dry-run gate gets pre-registered, executed, and logged to the ledger as usual. 

*Result:* Within a few hours, you will have a dataset containing representatives from SNNs (`spike_integration`), standard MLPs (`instantaneous`), and energy models (`em`/`ps`), complete with their `credit_trace` and `settle_horizon` instrument readings.

---

### Phase 2: Feature Engineering for High-Dimensional Visualization
To make t-SNE/UMAP work on categorical algorithmic configurations, you must translate the 6-D ontology into a continuous/vector space.

Create a script `scripts/visualize_atlas.py` that processes the SQLite/JSONL ledger:
1. **One-Hot Encode the Axes:** Convert Dynamics, Credit, Update, and Topology into binary vectors.
2. **Calculate Derived "Physics" Metrics:**
   * **BP-Deficit:** `Ruler_Ceiling - Measured_Accuracy`. (How far is this local rule from the global optimum?)
   * **Compute Efficiency:** `Accuracy / Training_Time`.
   * **Stability Margin:** Use the `spectral_radius` ($\rho$) or `settle_horizon` from the instrument logs.
   * **Gradient Alignment:** The cosine similarity from the `credit_trace` instrument.
3. **Concatenate:** Combine the one-hot vectors and the continuous physics metrics into a single high-dimensional feature vector for each cell.

---

### Phase 3: The "Crystallizing" Visualizations
Generate an interactive HTML dashboard (using Plotly or Streamlit) featuring these three specific views. This will serve as your primary demonstration artifact.

#### 1. The "Islands and Voids" Map (UMAP / t-SNE)
* **What it is:** A 2D scatter plot of the UMAP embedding of your feature vectors.
* **How to style it:** 
  * Color points by **BP-Deficit** (Red = high deficit/failure, Blue = low deficit/success).
  * Shape points by **Dynamics Family** (e.g., Circles for `em`, Triangles for `ps`, Stars for `spike_integration`).
* **The "Wow" Factor:** You will visually see distinct "islands" of algorithmic families. More importantly, you will see massive empty spaces. You can overlay the `structural_voids.jsonl` data as faint grey dots to show the "ghost topology" of the space—the combinations that the ontology allows but physics/geometry forbids.

#### 2. The "River of Computation" (Parallel Coordinates Plot)
* **What it is:** A Plotly Parallel Coordinates chart where each vertical axis represents an ontology dimension (Dynamics $\rightarrow$ Credit $\rightarrow$ Update $\rightarrow$ Topology $\rightarrow$ Accuracy).
* **The "Wow" Factor:** This visually crystallizes the *interaction effects*. You will literally see the "rivers" of high performance. For example, you might see a thick blue river flowing from `predictive_settling` $\rightarrow$ `thermodynamic_contrast` $\rightarrow$ `lion` $\rightarrow$ `feedforward`, while a red river shows `instantaneous` $\rightarrow$ `local_goodness` dying out at depth 8.

#### 3. The Instrument Radar (Spider Charts)
* **What it is:** Select the top 3 "Pareto-optimal" cells discovered in the broad sweep. Plot their instrument readings (`credit_trace` alignment, `settle_horizon`, $\rho(J_F)$, BP-Deficit) on a radar chart.
* **The "Wow" Factor:** This proves that the system isn't just finding high accuracy by luck; it proves *why* they work based on the physical instruments you built in Phase 0.

---

### Phase 4: Packaging the Demonstration
Wrap this into a single CLI command to make it reproducible and presentable.

```bash
comp gallery --generate-broad-demo --epochs 1 --sample-size 500
```

**The Narrative for your Demo/Paper:**
When presenting this, lean into the unique philosophy of Computronium:
1. **The Map is the Result:** "We didn't just find a new algorithm; we mapped the physical constraints of local learning. The voids in our t-SNE are just as important as the islands—they represent structural impossibilities."
2. **Instruments over Black Boxes:** "Notice how the UMAP clusters aren't just grouped by accuracy, but by their *gradient alignment* and *settling horizons*. Our instruments prove that `predictive_settling` forms a distinct physical regime compared to `energy_minimization`."
3. **The BP-Deficit Frontier:** "By mapping the BP-Deficit across 500 random coordinates, we have empirically defined the exact boundary where local, biologically plausible credit assignment can compete with global backpropagation."

### Immediate Next Steps for You:
1. Write the `broad_mapping_sweep.py` script using `random.choice` over the registries, stratified by Dynamics.
2. Ensure the `dry_run_gate` catches the shape mismatches so you don't pollute your CEEC ledger with execution errors.
3. Install `umap-learn` and `plotly` in your `uv` environment.
4. Run the sweep, export the data to a Pandas DataFrame, and generate the UMAP. 

This approach bypasses the current engineering blockers, respects the project's rigorous epistemic standards, and delivers exactly the kind of high-impact visual proof-of-concept you are looking for.

---

## Implementation Record (2026-09-15)

All four phases are implemented and smoke-verified end-to-end (task
`digits`, 1 epoch: 4 measured cells + 7 structural voids → `atlas.html`).

### Phase 1 — `scripts/broad_mapping_sweep.py` ✅
- `StratifiedRandomDriver`: proposes uniform-random grid cells
  (`GRID_DYNAMICS × GRID_CREDITS × GRID_UPDATES × GRID_TOPOLOGIES`),
  stratified so the **least-proposed dynamics family is always sampled
  next** (perfect balance in the proposal stream). Novelty = in-process
  cell-key set **seeded from the KB coverage matrix**, so resumed runs do
  not re-measure cells the G1 sweep covered (voids included — a void is
  covered, it can never execute).
- `BroadMappingCampaign(AutoScientistCampaign)`: overrides
  `_record_incompatible` to append every dry-run-rejected cell to
  `structural_voids.jsonl` (task/dynamics/credit/update/topology/error) in
  addition to the base KB cover-marking. The CEEC ledger sees **only**
  gate-passing cells (pre-register → execute → record), per the epistemic
  rule.
- Stops on `--sample-size` measured cells or `--max-iterations`; artifacts
  under `artifacts/broad_map/` (`kb.sqlite`, `ledger.sqlite`,
  `structural_voids.jsonl`, campaign DB).
- Note: the campaign layer already had the dry-run gate + void cover-marking
  (TODO27 rev 4/rev 5) — this script only adds the stratified sampler and
  the voids JSONL side-channel.

### Phase 2+3 — `scripts/visualize_atlas.py` ✅
- Reads measured cells from the KB (`experiment:<task>` entries →
  dynamics/credit/update/topology hyperparameters + accuracy/loss metrics)
  and voids from `structural_voids.jsonl`.
- Features: one-hot over the four sampled axes + continuous
  (accuracy, BP-deficit). **BP-deficit = ruler ceiling − measured accuracy**
  from `artifacts/ruler_table.json` (per-task `bp_val_accuracy`).
- Embedding: UMAP (umap-learn added to main dependencies) with sklearn
  t-SNE fallback; deterministic seed 0.
- One HTML (`atlas.html`) with the three views:
  1. Islands & Voids — scatter colored by BP-deficit, symbol per dynamics
     family, voids overlaid as faint grey points ("ghost topology").
  2. River of Computation — parallel coordinates (dynamics → credit →
     update → topology → accuracy), colored by accuracy.
  3. Instrument Radar — top-3 Pareto cells (non-dominated on maximize
     accuracy / minimize deficit) over the available continuous metrics.

### Phase 4 — `comp gallery --generate-broad-demo` ✅
- `computronium/cli/gallery.py`: `--generate-broad-demo --epochs 1
  --sample-size 500` runs the sweep then the atlas render (defaults per
  plan). README CLI table updated.

### Deviations / honest limitations
- **Instrument readings not yet in the atlas**: the campaign executor's
  result dict carries accuracy/loss only — no `credit_trace` gradient
  alignment, `settle_horizon`, or ρ(J_F). The radar substitutes available
  metrics (accuracy, train_accuracy, 1−deficit, 1/(1+loss)); it proves
  Pareto optimality, not yet the "why" (plan §3.3's wow factor is
  unrealized until instruments are recorded per cell).
- **Compute Efficiency** (`accuracy / training_time`) dropped: wall-time is
  not recorded in the result dict. Same fix path as above.
- One-hot × void overlay: voids embed via their one-hot axes only (no
  metrics); their grey positions are structure-only coordinates.

### Preliminary production run (2026-09-15, walltime-skewed host)
31 measured cells + 43 structural voids on `digits` @ 1 epoch
(`artifacts/broad_map/`, `logs/broad_map_prelim.log`; run under
background load, so **no wall-time metrics were used** — the map is
accuracy/BP-deficit only). Static figure pinned to
**`docs/figures/d28_broad_atlas.png`** (via `visualize_atlas.py --png`);
interactive dashboard at `artifacts/broad_map/atlas.html`.
Preliminary shape already legible at n=31:
- **Islands**: `em` max 0.886, `instantaneous` 0.856, `ps` 0.867 —
  three distinct viable regimes at the ruler ceiling's doorstep.
- **Voids**: `diffusion` 0/5 cells executed (100% void), `lazy` 12/14 —
  the structural-impossibility finding is real, not a sampling artifact.
- `spike_integration`/`error_predictive_coding` at 0.647 — mid-field,
  consistent with credit × topology constraints rather than failure.

### Pre-extended-run audit (2026-09-15)
All 43 voids classified (new `category` field in `structural_voids.jsonl`,
`classify_void` in the sweep script; existing rows backfilled):
- **35 `geometry_constraint`** — genuine ontology boundaries (em/ePC need
  layered geometry, lazy restrictions, local_contrastive linear-stack).
  Verified em × recurrent *executes*, so the EqProp contract is intact.
- **7 `settle_route_shape`** — implementation boundary, NOT physics:
  spike/ps settle passes raw `[b, features]` states into
  `AttentionGeometry.route` (geometry.py:2006) / `SpatialLattice3DGeometry.route`
  (geometry.py:2279), which assume settle-state shapes. Layered geometries
  tolerate 2-D; these two do not.
- **1 `autograd_break`** — `diffusion × gradient`: diffusion settle returns
  a non-differentiable state; `BackpropCredit.compute_pseudo_gradient`
  crashes.

**Verdict: safe to extend now.** Crash-class voids are caught by the
dry-run gate in seconds — no budget pollution, no wasted training. The
category field lets the atlas narrative separate physics voids from
implementation boundaries. Deferred fixes (post-campaign, they *expand*
the measurable grid):
1. Non-layered `route()` should accept `[batch, features]` settle input
   (reshape/project) — reopens spike/diffusion/ps × attention/lattice.
2. Diffusion settle differentiability for gradient credit (or a documented
   credit whitelist branch in `SystemConfig.validate()`).
3. **Stale-rule contradiction**: `validate()` forbids spike ×
   non-temporal credit, yet spike × `local_contrastive` executed and hit
   0.647 (chance 0.1). Either the rule is stale or the path is degenerate —
   investigate before trusting either the rule or the cell.
4. Note: `compose_system_from_configs` (factory.py:576) never calls
   `SystemConfig.validate()` — the campaign path is gated only by the
   dry-run gate. Enforcing validate() as-is would *forbid* the measured
   spike × local_contrastive cells; resolve finding 3 first.

### Bug-fix pass — "nothing is sacred" (2026-09-15, invalidates prior results)
All preliminary artifacts (`artifacts/broad_map*`,
`docs/figures/d28_broad_atlas.png`) were **deleted and regenerated** after
these fixes; earlier numbers in this file are historical.

1. **`SystemConfig.validate()` now enforced in the campaign compose path**
   (`compose_cell_system`, autoscientist/compose.py) — previously the
   AutoScientist path skipped it, executing cells validate() forbids
   (spike × thermodynamic_contrast ran at chance) and relying solely on
   the dry-run gate.
2. **Stale rule 1 relaxed on measured evidence**: recurrent geometry now
   accepts `predictive_settling` (measured 0.867) and
   `error_predictive_coding` (0.647) and `instantaneous` (single forward
   pass, topology-agnostic) — the old "recurrent requires
   energy_minimization" rule contradicted four measured cells.
3. **New state-shape branch**: `spike_integration`/`diffusion`/
   `predictive_settling` × {attention, spatial_lattice, graph, conv} →
   hard reject — these settling families feed raw membrane states into
   `geometry.route()`, which those geometries cannot accept (the 7+2
   crash-voids). Converted from dry-run crashes to clean constraint
   voids.
4. **New diffusion/gradient branch**: diffusion settle is a detached
   Langevin sampler (by design — `h.detach()` per step); gradient/backprop
   credit has no graph to consume → hard reject instead of autograd crash.
5. **`classify_void` keywords extended** to cover every validate() message
   (PC credit rules, tile_mesh rule) — void ledger is now fully
   categorized.

**Known deeper defect, deferred (recorded honestly):**
`DiffusionDynamics.compute_energy_from_state` is geometry-independent —
`h.pow(2).sum() + beta*||h-target||²` never reads geometry weights, so
diffusion "settling" is a prior-only random walk regardless of topology.
Redesigning it (a real Langevin energy over the geometry) is a dynamics-
research task, not a campaign blocker; diffusion cells in the atlas are
measurements of that degenerate sampler until fixed.

Verification: 5 must-compose cells pass (incl. previously-forbidden
ps × recurrent, ePC × recurrent), 3 must-reject cells raise clean
ValueErrors; `test_campaign_fidelity` + `test_dynamics_wiring_lock`
(28 passed); validate/compose/campaign/scientist test slices green;
ruff + pyright strict clean on all touched files.

**Post-fix preliminary map** (31 cells, 123 voids, `digits` @ 1 epoch,
`docs/figures/d28_broad_atlas.png` regenerated): **123/123 voids
classified `geometry_constraint`, 0 crash-class** — the atlas now shows
pure ontology boundaries. Islands: `ps` 0.950, `instantaneous` 0.881;
`lazy` at 0.581 (was chance in the pre-fix run — the old run's chance
cells were the unenforced-rule artifacts this pass removed). `em` 0.644
and `spike` 0.175 are 1-epoch/lr variance at tiny n — not signals.
Sampling note: valid ePC cells have ~13% draw probability (credit ×
topology rules), so 0 ePC cells at n=31 is unlucky, not structural.

### Ontology coverage audit + parameter fairness (2026-09-15, pre-extended-run)
Audit findings and fixes — "are we covering ALL of the ontology, fairly?"

**Coverage (per axis, Digital substrate only):**
- Dynamics 7/7 ✓, Credit 9/9 ✓.
- Update: was 9/12 — added `riemannian_orthogonal`, `unit_rms`
  (bare-cell composable); `role_split` stays excluded (needs role
  metadata, not parameterizable as a bare cell).
- Geometry: `build_geometry_config` gained `causal_transformer`; the
  grid now spans 6 topologies {feedforward, recurrent, tile_mesh,
  attention, spatial_lattice, ntm}. Excluded as **task-shape-
  specialized** (factories need inputs flat classification cannot
  supply): `conv` (spatial H×W, hardcoded 28×28 default), `nca`
  (channels×grid == input_dim), `causal_transformer` ([B, T] int64
  token ids), `graph` (explicit edge_index).
- **P-axis (plasticity) still absent** — the sweep is the 5-D
  `M = NullPlasticity` slice. Wiring plasticity configs into grid cells
  (compose path + validate branches) is the biggest remaining coverage
  gap; deferred as its own work item, not a blocker for the 5-D map.
- New hard rule discovered by the wider net: **only `instantaneous`
  composes with non-layered geometries** {attention, spatial_lattice,
  graph, conv, nca, ntm, causal_transformer} — every settling family
  crashes there (attention head-split, lattice (b,n,c) unpack). Now a
  validate() branch.

**Parameter fairness:**
- Fixed depth=2/hidden=64 spans **~400×** in geometry params (conv
  3.8K → spatial_lattice 1.63M). Added `param_budget` (default 25K):
  the executor iteratively rescales `hidden_dim` (≤3 rounds, ±25%
  target) and every measured cell now records `param_count` (33/33
  recorded). Converged: feedforward 19.3K, recurrent 22.2K,
  spatial_lattice 47.6K (lattice's input-projection dominates; 1.9×
  over budget — residual confound, noted for analysis).
- **Enumerated constraint map**: the full 4158-cell product through
  `SystemConfig.validate()` → **1111 viable / 3047 voids (73%
  structurally impossible)**, written to `structural_voids.jsonl` for
  free (no GPU). The sampler now draws only viable cells — governed
  budget never proposes known-rejected coordinates.

**Post-fix verification map** (34 viable cells, digits @ 1 epoch,
`docs/figures/d28_broad_atlas.png`): lazy 0.942, ps 0.922, spike 0.911,
ePC 0.858 — four families at the ceiling. Anomalies to watch in the
extended run: `em` 3 cells max 0.111 and `instantaneous` 3 cells max
0.242 (earlier runs measured 0.86-0.94) — either degenerate credit ×
update draws at 1 epoch or a rematch/lr interaction; resolve with
volume, not speculation. attention/ntm/tile_mesh drew 0 cells (rare
viable density); extended run fills them.

**Answer to "more preliminary experiments first?"**: yes — three, all
cheap: (1) this enumeration (done, reusable), (2) an lr calibration
pass for non-feedforward topologies (`_ruler_lr` gives them a
conservative 1e-3 flat default — a topology-lr confound), (3) a
~100-cell viable-only pilot to check param-rematch convergence and the
em/instantaneous anomaly before committing the 500-cell run.

### Immediate items (next session, in this order)

1. ~~Resolve the `em`/`instantaneous` anomaly — BLOCKING.~~
   **RESOLVED (2026-09-15): param rematch exonerated.** Paired probe
   (`scripts/probes/d28_rematch_lr_probe.py`, 7 em/inst × feedforward
   cells, budget 25000 vs 0): diffs −0.033…+0.081 with no systematic
   sign; the strong cell (em|local_goodness|riemannian_orthogonal 0.867)
   holds *with* rematch at healthy settle horizon (30) and ρ (0.067).
   The anomaly was **credit × update draw composition**:
   target_inversion / homeostatic / temporal_trace / elastic_consolidation
   cells sit at chance (0.08–0.17) regardless of budget or lr. The
   34-cell verification map's 3 em + 3 instantaneous draws were
   degenerate credit/update pairs. Resolved by volume in the 500-cell
   run; stratifying credit × update pairs (improvement 2) would prevent
   recurrence at small n.
2. ~~Instrument capture.~~ **DONE (2026-09-15).**
   - Every settle implementation now records
     `_settle_steps_used` via a shared `_SettleTelemetry` mixin
     (dynamics/_dynamics.py) — em's compiled/checkpointed/eager paths,
     ps (tile/layered/recurrent), ePC, spike, diffusion, lazy
     (convergence break counts steps), instantaneous (1).
   - `probe_spectral_radius` in campaign.py: sampled directional
     amplification ‖Jv‖ of the free-settle map (fast-proxy semantics;
     the settle map is dimension-changing so ρ(J) is undefined —
     documented honestly). 0.0 on settle failure.
   - `_execute_proposal` result dict now carries `spectral_radius`,
     `settle_horizon`, and `lr`; they flow into the KB metrics
     automatically (numeric-key passthrough).
   - `visualize_atlas.py`: AtlasRow/load_cells carry the new metrics;
     the radar appends `settle_horizon` and `σ_max(J)` spokes
     (min-max normalized over the Pareto set, shown only when nonzero).
   - Consolidation: `analysis/instruments.py::settle_horizon` now reads
     the canonical `_settle_steps_used` telemetry (was free-energy
     history length) — also fixes a pre-existing
     `test_settle_caller_census` failure (bare settle call there).
3. ~~lr calibration for non-feedforward topologies.~~
   **DONE (2026-09-15) — default changed 1e-3 → 1e-2.** Probe
   (`scripts/probes/d28_topology_lr_probe.py` + known-good follow-up):
   the flat 1e-3 default **starved every non-feedforward cell** —
   recurrent em|local_goodness 0.161 @ 1e-3 vs **0.856 @ 1e-2**;
   tile_mesh 0.25→0.286 @ 1e-2; instantaneous feedforward 0.075 @ 1e-4
   vs 0.478 @ 1e-3. No topology preferred a smaller lr.
   `_ruler_lr` now returns 1e-2 for non-feedforward (docstring cites
   the probe); `test_ruler_lr_scoping` updated.
   **New defect found and fixed en route:** the executor fed raw 4-D
   vision batches `(B, C, H, W)` into systems composed for flat
   input_dim — credit/view reshapes crashed (mat-mismatch, ntm
   `(32, 8, 8)`). `SystemTrainer` now canonicalizes `x` to `(B, -1)`
   at both the train and validate boundaries. Still-open crash: ntm
   mixes a CPU tensor into a CUDA graph (ntm-geometry device defect,
   deferred — one topology).
4. **The 500-cell run** — unblocked by 1–3:
   `nohup uv run comp gallery --generate-broad-demo --sample-size 500 >
   logs/broad_map_500.log 2>&1 &` with the AGENTS 2-min poll cadence.

**Explicitly deferred:** P-axis 6-D expansion (own campaign, after the
5-D map ships); diffusion's geometry-independent energy defect (recorded
below); surrogate model (stratified mapping bypasses it by design).

### Deferred items addressed + 50-cell pilot (2026-09-15, session 3)

"Nothing is sacred" pass — the two deferred defects were blocking-class
and are now fixed; the pilot ran only after both landed.

1. **Diffusion geometry-independent energy — FIXED.** The old
   `compute_energy_from_state` was `‖h‖²` (+ β one-hot pull) — the
   Langevin "settle" never read geometry weights: a prior-only random
   walk, identical statistics on every topology. Layered path now
   descends the **em-family Hopfield energy through the geometry's
   weights** over the full activation stack (Langevin: `dh = −∇E dt +
   √(2·D)·dW`, input clamped) + β output nudge — a stochastic sampler
   over the geometry's fixed points (noisy em), producing per-layer
   acts the credit rules can consume. Documented prior-only fallback
   remains for non-layered geometries (unreachable via the campaign
   grid). Pilot evidence: diffusion max accuracy 0.086 → **0.425**
   with the fix (still last at 1 epoch — plausible for a stochastic
   sampler, not a crash).
2. **`credit_trace` per-cell capture — DONE.** Opt-in
   (`--credit-trace` → `hyperparams["credit_trace"]`): one flat batch
   on the system's device, settle phases + split-half + BP reference;
   `credit_alignment` (min per-layer BP cosine) flows into the result
   dict → KB → radar spoke.
3. **Device-poisoning class, found by the pilot, fixed at the source.**
   Cells are dry-run-probed on CPU before the trainer moves geometry to
   the accelerator; any credit that lazily initializes per-weight state
   on first contact stranded it on CPU and crashed at train time:
   - FA feedback matrices (`RandomProjectionsCredit`):
     `_sync_feedback_device` re-homes cached matrices onto the weight
     device per pseudo-gradient read.
   - LocalContrastive/TemporalTrace EMA cache: `_ema_normalize` moves
     cached tensors to the incoming gradient's device.
   - `_block_target_grads` zero-grad placeholder: created on the acts'
     device.
   - ntm `init_mem/init_state/prev_read` were the same class (fixed
     earlier this session).
4. **Resume-blocking bug in the sweep itself**: `enumerate_constraint_
   voids` called `.strip()` on the *parsed* void dict — any run
   restarting against an existing `structural_voids.jsonl` crashed at
   startup. Fixed (strip the line, then parse). The device fixes were
   validated by a smoke sweep (6/6, 0 device failures) before launch.

### Pilot results (52 fresh cells, digits @ 1 epoch; 82 unique in KB
with the earlier partial run — a background process died mid-iteration
on the flaky host and the resumed run continued seamlessly from KB
coverage, which is the resume path working as designed).

**Zero failed proposals** after the device fixes (4 iterations of the
killed run had device crashes; the fixed run: none). All 7 families
sampled:

| family | n | max | mean |
|---|---|---|---|
| predictive_settling | 12 | 0.942 | 0.759 |
| instantaneous | 10 | 0.961 | 0.565 |
| error_predictive_coding | 12 | 0.881 | 0.504 |
| lazy | 12 | 0.944 | 0.321 |
| spike_integration | 11 | 0.864 | 0.383 |
| energy_minimization | 12 | 0.922 | 0.300 |
| diffusion | 13 | 0.425 | 0.118 |

- Six of seven families reach the ruler ceiling's doorstep — the
  post-fix ontology composes and trains nearly everywhere it validates.
- `credit_alignment` recorded for 63/82 cells (n=0 where the credit
  reaches no learnable weight — itself an instrument signal); max 0.978
  (gradient-class credit ≈ BP, as the instrument predicts).
- diffusion's fix shows real (0.086 → 0.425 max) but stays last at
  1 epoch — expected for a noisy sampler; judge at more epochs, not by
  crash-class absence.
- Artifacts: `artifacts/broad_map_pilot50/` (kb, ledger, voids 3051,
  `atlas.html`), `docs/figures/d28_broad_atlas.png` regenerated at
  n=82 measured cells.

**Decision the pilot informs:** family-level maxima are stable across
re-runs (ps/inst/em/lazy/spike within noise of prior runs); mean-level
separation is now dominated by credit×update composition — the 500-cell
run can proceed with `--credit-trace` for the full instrument set, and
stratification beyond dynamics (improvement 2) is the next lever before
any small-n claims.

### Defect convergence + runtime-contract gate (2026-09-15, session 3 close)

The suite never caught the device class because it exercised the
ontology's *logic* (CPU, synthetic input) while every bug lived in the
*runtime contract* (CPU probe → GPU train, real batch shapes). That
contract is now encoded:

- **`tests/property/test_device_hygiene_gate.py`** — all 429 viable
  feedforward cells: compose → CPU train_step (forces every lazy
  init a dry-run/probe would trigger) → `geometry.to(cuda)` → train
  step. Would have caught every device bug pre-pilot; it found one
  more subclass post-fix.
- **`update.py` momentum buffers** — `_fresh_buffer` re-inits on
  device change (zero-warm-start, lossless) at every cache site; the
  gate went 312 failing → 429/429.
- Property suite re-run after the gate: 761 passed, no regressions.

**State:** defects in the experimental path are gated (composition =
validate + enumeration; execution = hygiene gate; numeric health =
per-cell instruments; resume = KB coverage seed). Known limitations
(documented, non-corrupting): diffusion slow at 1 epoch, σ_max(J) is a
sampled lower bound, surrogate bypassed by design, P-axis out of grid.
Next action unchanged: the 500-cell run with `--credit-trace`.

---

## Current State Summary (2026-09-15, post-pilot)

### ✅ Implementation Complete — All 4 Phases
| Phase | Deliverable | Status | Location |
|-------|-------------|--------|----------|
| 1 | Stratified random sweep + void ledger | **Done** | `scripts/broad_mapping_sweep.py` |
| 2 | Feature engineering (one-hot + BP-deficit + instruments) | **Done** | `scripts/visualize_atlas.py` |
| 3 | Three-view HTML atlas (UMAP, parallel coords, radar) | **Done** | `scripts/visualize_atlas.py` |
| 4 | CLI command `comp gallery --generate-broad-demo` | **Done** | `computronium/cli/gallery.py` |

### ✅ Pre-Run Blockers Resolved
1. **em/instantaneous anomaly** → credit×update draw composition (resolved by volume)
2. **Instrument capture** → settle_horizon, σ_max(J), credit_alignment now per cell
3. **Topology lr confound** → default 1e-3 → 1e-2 for non-feedforward (probe-verified)
4. **Diffusion energy defect** → now descends geometry Hopfield energy
5. **Device-poisoning class** → all lazy inits re-home to weight device
6. **Sweep resume crash** → `.strip()` on line before parse

### ✅ Verification Gates Passing
- `test_campaign_fidelity` + `test_dynamics_wiring_lock` (28 passed)
- `test_device_hygiene_gate` (429/429 viable feedforward cells pass)
- validate/compose/campaign/scientist test slices green
- ruff + pyright strict clean on all touched files

### 🔄 Next: 500-Cell Production Run (Execution, Not Implementation)
```bash
nohup uv run comp gallery --generate-broad-demo --epochs 1 --sample-size 500 --credit-trace > logs/broad_map_500.log 2>&1 &
```
- Uses 1111 viable cells (enumerated from full 4158 grid, 73% void)
- Stratified by dynamics (7 families), draws from viable set only
- Captures full instrument set per cell (settle_horizon, σ_max(J), lr, credit_alignment)
- Resume-safe: KB coverage seeds seen-set, voids JSONL append-only
- Est. walltime: 2-4 hours GPU (em/ps settling dominates)

---

## Improvement Opportunities (Facilitating Remaining Work)

### 1. Stratification Beyond Dynamics (Code Change) — **DONE (2026-09-15)**
**Priority: High** — the anomaly diagnosis showed degenerate credit×update draws were the em/instantaneous "collapse" at small n. The current `StratifiedRandomDriver` only balances dynamics; extend to balance credit × update pairs so no river axis starves at small sample sizes.

**Location:** `scripts/broad_mapping_sweep.py` → `StratifiedRandomDriver.propose_batch()`
- Balance now tracked per `(dynamics, credit, update)` triple (not just dynamics)
- Proposes least-proposed triple first, ensuring even coverage across all river axes
- Log shows balance sample per triple at each iteration

### 2. Multi-Task Atlas — **DONE (2026-09-15)**
**Priority: Medium** — `load_cells` filters by `experiment:<task>`; add a task facet (color/animation frame) once multi-task sweeps run.

**Location:** `scripts/visualize_atlas.py`
- `load_cells(kb_path, task=None)` loads all tasks when `task=None`, includes `task` column
- `--multi-task` flag enables multi-task visualization
- Islands plot: color by task, symbol by dynamics (legend grouped by dynamics)
- Feature matrix includes task one-hot when multi-task enabled
- BP-deficit computed per-task against ruler ceiling

### 3. Gallery Lock (Demo Checklist)
**Priority: Low** — if the broad demo ships as a gallery figure, follow the `_ARMS` static-table pattern + `docs/figures/manifest.json` re-pin (AGENTS demo checklist). Not done here (HTML artifact, not a PNG demo).

### 4. P-Axis 6-D Expansion
**Priority: Deferred** — biggest remaining coverage gap (plasticity configs wired into grid cells). Own campaign after the 5-D map ships.

### 5. σ_max(J) Certification
**Priority: Low** — radar's σ_max(J) is a sampled directional amplification (fast proxy), not a certified radius. Documented honestly in code.

### 6. Diffusion at More Epochs
**Priority: Low** — diffusion's fix shows real improvement (0.086 → 0.425 max) but stays last at 1 epoch. Judge at more epochs, not by crash-class absence.

### 7. Non-Layered Route() Reshape (Expands Measurable Grid)
**Priority: Deferred** — `AttentionGeometry.route` / `SpatialLattice3DGeometry.route` assume settle-state shapes; accept `[batch, features]` to reopen spike/diffusion/ps × attention/lattice.

### 8. Diffusion Settle Differentiability for Gradient Credit
**Priority: Deferred** — or a documented credit whitelist branch in `SystemConfig.validate()`.
