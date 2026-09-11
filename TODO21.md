# TODO21 — Platform Afterlife: Publication, Hygiene, and Honest Boundaries

**Status:** NOT STARTED. Read §12 Progress log first once work begins — it carries completed-state, gotchas, and environment notes.
**Created:** 2026-09-11
**Supersedes:** TODO20 (closed 2026-09-11 — all DoD checked, Rule 6 satisfied, audit clean)
**Absorbs:** All registered-but-unfixed TODO20 improvement opportunities and deferred-science boundaries that still have product value

## 0. Charter

TODO20 shipped the platform (5 packages, single-source, audited). TODO21 has
three aims, in payout order:

1. **Publication** — turn the released mechanisms into a submitted paper.
2. **Hygiene closure** — retire Register C debt AND the residual extraction
   dedup/integration debt (Phase 3A) so the repo is cheap to grow.
3. **Boundary-gated science** — only run experiments that unblock a released
   recipe or a publication claim (harvest-only rule, TODO20 Rule 1, still
   binding).

Operating rule (inherited):

> No new internal knowledge accumulation unless it directly supports the
> publication, a release-blocking defect fix, or a required hygiene closure.

Non-goals: new ontology axes, new ledger features, new packages, hardware
purchases, large-scale benchmarking, universal claims.

---

## 1. Phase 1 — Publication Track (highest leverage)

### T21.1.1 Pick a venue and freeze the claim set
- Decide target (e.g., workshop track: NeurIPS/ICLR workshops on scientific
  ML / local learning; or a methods journal).
- Output: `docs/platform/PUBLICATION_VENUE.md` — venue, deadline, page
  limit, which 4 mechanisms are in scope, which are cut.
- Constraint: claims limited to what MECHANISM_RECIPES.md documents; any new
  claim needs a pre-registered experiment first (G-RELEASE-5 discipline).

### T21.1.2 Expand the draft into a full manuscript
- File: `docs/platform/PUBLICATION_DRAFT.md` → promote to
  `docs/platform/MANUSCRIPT.md` (draft stays as outline provenance).
- Sections per the outline: ontology framing, CEEC protocol, mechanisms
  1–4, boundaries/falsified branches, hardware blueprint (simulation-only),
  reproducibility statement.
- Include threats-to-validity verbatim from the outline.
- Figures: reuse registered artifacts (`docs/figures/registered/`); generate
  new figures via gallery patterns only (manifest-locked).

### T21.1.3 Reproducibility package
- One command per reviewer claim: verify `uv sync --dev --all-extras` +
  quick-mode demos/benchmarks reproduce every number cited in the
  manuscript. Add `docs/platform/REPRODUCIBILITY.md` mapping each claimed
  number → command → registered artifact/evidence id.
- Gate: a fresh-clone dry run (no cached venv) completes in one session.

### T21.1.4 Claim-discipline audit of the manuscript
- Extend `tests/platform/test_release_docs.py` banned-phrase scan to
  MANUSCRIPT.md; extend scope/limitation section checks.

**Acceptance:** manuscript exists; every number traceable to a command and
an evidence id; claim checks pass.

---

## 2. Phase 2 — Boundary-Gated Science (only what unblocks Phase 1/recipes)

### T21.2.1 B-H3 promotion flow
- The stable-amplification belief still fails the `probability_threshold`
  gate post X-STA-002. Options (pick one, document):
  - run the boundary-gate evaluation path (declare the validated scope as
    the boundary) and mark the belief `bounded` if the machinery supports
    it;
  - or add one more cheap probe (e.g., noise-level sweep extension of
    x_sta_002) to clear the threshold honestly.
- Do NOT relax the gate. X-STA-002 lesson: noise divergence scales with the
  same ratio as retention — the belief interval [0.55, 0.85] must reflect
  retention-gain-only, not SNR.

### T21.2.2 X-USU-002 defect hunt (conditional)
- Condition: run ONLY if the RoleSplit recipe is load-bearing for the
  publication's heterogeneous-hardware story.
- Pre-register first (`configs/ceec/experiments/`), axes
  update_arm × batch_size × smoothing × seed; mirror x_usu_001 structure.
- Deliverable: defect explanation or explicit boundary added to the recipe
  and recipe book. No boundary without the hunt.

### T21.2.3 X-RSE baseline (conditional)
- Condition: run ONLY if a routing recipe is wanted for the paper.
- Fix the dense baseline learnability (lengthen budget or simplify task),
  re-run X-RSE, and only then X-RSE-002 at matched effective ops.
- If the baseline still cannot beat chance, restate the boundary in
  EXTERNAL_SUMMARY and stop.

---

## 3. Phase 3 — Hygiene Closure (Register C)

### T21.3.1 `ActivityValue` union narrowing
- Single fix in `packages/stability/src/stability/state.py`: replace the
  loose `Tensor | list[Tensor] | float | dict[str, float]` union with a
  discriminated access-helper API; update lyapunov/settling/basin call
  sites in the SAME pass (~70 basic-mode errors expected to clear).

### T21.3.2 Per-package pyright configs
- Add `pyrightconfig.json` to `packages/*` that need script/example gating
  (resolves TODO20 opportunity #8: root config overrides member
  `[tool.pyright]` sections).

### T21.3.3 Single-command test gate
- If desired: prefix package test basenames (`test_psi_*`, `test_lf_*`,
  `test_stab_*`, `test_lab_*`) or move packages to importlib mode, then run
  one pytest invocation across all suites. Migrate `tests/ceec/*` off the
  `from conftest import ...` pattern FIRST (TODO20 opportunity #5).

### T21.3.4 Lab de-coupling (small)
- Stable trainer-metrics contract so `Lab.train` stops hardcoding history
  keys (opportunity #15).
- Wire per-epoch history through `ComparisonResult` (opportunity #16) if
  curve evidence moves into Lab.

### T21.3.5 Repo-wide gates (round close only)
- `ruff check` repo-wide, `pyright .` repo-standard, full `pytest`,
  `pip-audit`. Close or explicitly re-queue every finding — no silent skip.

---

## 3A. Phase 3A — Platform Integration & Deduplication (Rule 6 extended)

Residual dedup/integration debt from the TODO20 extractions, plus the next
round of useful extractions. Surveyed 2026-09-11; judgments recorded so
future work does not re-litigate.

### Dedupe — internal code must consume the packages

- [ ] **T21.3A.1 Metrics single-source** — `computronium/analysis/mechanistic_study.py`
  (inline `improvement_per_norm`) and `computronium/analysis/dynamics.py`
  (inline cosine-alignment) re-implement statistics that live in
  `local_feedback/metrics.py` and `psi_peft/metrics.py`. Import from the
  packages; delete the inline copies; keep the parity tests green.
- [ ] **T21.3A.2 Power-iteration single-source** —
  `computronium/core/spectral_mixin.py`,
  `core/optimization/strategies/constraint.py::_power_iteration`, and
  `acceleration/contrastive_primitives.py::spectral_norm_power_iteration`
  each hand-roll power iteration that `stability.spectral_radius` already
  ships. Route through the package (extend its API if a tensor-in/tensor-out
  helper is missing — one addition, not three).
- [ ] **T21.3A.3 Synthetic-task factory** — 5+ near-identical
  gaussian-blob/switching task builders (`experiments/joint/*`,
  `computronium_lab/lab.py`, `psi_peft.metrics.SyntheticTask`). Land one
  factory (candidate: a `domains` helper in Lab or a shared tasks module)
  and delete the copies.
- [ ] **T21.3A.4 Local state lookalikes** —
  `experiments/joint/adaptation_efficiency.py` / `compute_efficiency.py`
  define private "simple composite state" classes; import
  `computronium.state.CompositeState` instead.
- [ ] **T21.3A.5 Context/state name collapse** — three `SystemContext`
  definitions (empty Protocol in `stability.state`, rich dataclass in
  `computronium/state/context.py`, third in `computronium/core/joint/context.py`).
  Drop/rename the joint one and document the Protocol-vs-dataclass split —
  same name with three semantics is a footgun.
- [ ] **T21.3A.6 conftest mirrors production** — `tests/conftest.py`
  re-mirrors transition auto-discovery from `core/model.py`; import the
  production code instead.

### Integration direction decisions

- [ ] **T21.3A.7 Lab boundary** — `computronium-lab` imports
  `computronium.ontology/core` directly and has NO boundary test. Decide:
  (a) codify it as the sanctioned integration layer (add a boundary test
  asserting it may import computronium but packages must not import it), or
  (b) invert — move preset factories into the package. Record the decision
  in PLATFORM_LAUNCH.md either way.
- [ ] **T21.3A.8 Kill sys.path hacks** — 20+ probe scripts hand-roll
  `sys.path.insert(REPO_ROOT)`; `validation/tracks/*.py` append repo root
  from inside library code; `tests/conftest.py` too. Workspace editables
  make these dead — delete them (probes last, one commit, run the probe
  smoke set after).

### New extractions (each follows Rule 6: package is single source, adapters on legacy paths)

- [ ] **T21.3A.9 sqlite-ledger toolkit** — six hand-rolled sqlite stores
  (~3.9k LOC: `core/campaign/campaign_store.py`, `knowledge/{kb,vector_store,
  causal,metamodel,query}.py`, `hyperopt/storage.py`, `execution/_state.py`)
  re-implement schema-versioning/tx/id plumbing that `ceec.store` already
  has. Extract a shared base (or migrate stores onto ceec's primitives).
  Largest single consolidation available; do it store-by-store with parity
  locks.
- [ ] **T21.3A.10 spectral utilities** — if T21.3A.2 shows the package
  spectral module fits internal call sites, promote
  `stability.spectral_radius`/`matrices` as the canonical spectral kernel
  home; delete internal duplicates.
- [ ] **T21.3A.11 cli-toolkit** (optional) — shared argparse/db-path/tier
  plumbing (`computronium/cli/shared.py` pattern) reusable by package CLIs
  (`stability`, `ceec`); extract only if a second consumer appears.
- [ ] **T21.3A.12 figure-spec renderer** (optional) — the JSON figure-spec
  renderer in `visualization/_demo_api.py` is fully generic; extract if a
  second consumer (packages' demos) needs it (TODO20 opportunity #12).
- [ ] **T21.3A.13 execution scaffolding split** (optional, large) —
  framework-agnostic parts of `computronium/execution/` (`_state`,
  `lifecycle`, `events`, `monitoring`, `criteria`) could extract; engine and
  strategy stay (ontology-coupled). Only if a second consumer or publication
  artifact needs it.

**Acceptance:** every "dedupe" bullet above has its duplicate deleted (not
shimmed); extraction decisions (a/b) recorded in PLATFORM_LAUNCH.md;
boundary tests cover the decided directions; repo-wide ruff/pyright/pytest
still green after each store migration.

---

## 4. Phase 4 — Hardware Probe Sequence (optional, simulation-only)

From the edge blueprint's validation sequence — each is pre-registered,
quick-budget, and maps to a blueprint claim:

- **T21.4.1 Quantized ψ readout** — quantize psi_peft ridge statistics to
  int8/fixed-point; re-run the task-switching benchmark per-seed; record
  whether the validated pattern survives (publishable robustness line).
- **T21.4.2 Device-realistic feedback blend** — replace the EMA blend in
  local-feedback with a noisy/quantized update; re-run the X-ALI-002
  short-trajectory protocol.
- **T21.4.3 Substrate-noise replay** — inject bursty noise into the
  stable-amplification family; verify X-STA-002 paired-replay predictions
  (retention ratio ≈ noise-divergence ratio should persist).

Any falsification here feeds the blueprint's "what is NOT claimed" section
— that is a success outcome, not a failure.

---

## 5. Release Gates (inherited)

TODO20's G-RELEASE-0..6 gates apply to anything newly shipped. Claim
discipline (G-5) extends to the manuscript. Rule 6 (one copy) remains
binding for any new extraction.

## 6. Definition of Done

- [ ] Venue selected and claim set frozen (T21.1.1).
- [ ] Manuscript drafted with traceable numbers (T21.1.2/3).
- [ ] B-H3 promoted or boundary-gated (T21.2.1).
- [ ] X-USU-002 and X-RSE either executed or explicitly skipped with the
      condition recorded.
- [ ] `ActivityValue` union retired; stability estimators pyright-clean.
- [ ] Metrics/power-iteration/synthetic-task dedupes landed (T21.3A.1–3);
      internal analysis code consumes package metrics.
- [ ] Lab boundary direction decided + boundary test in place (T21.3A.7).
- [ ] sys.path hacks removed (T21.3A.8).
- [ ] sqlite-ledger toolkit extracted or explicitly deferred with rationale
      (T21.3A.9).
- [ ] Per-package pyright configs landed (if scripts need gating).
- [ ] Single-command gate green (if T21.3.3 adopted).
- [ ] Lab trainer-metrics contract (T21.3.4) or documented deferral.
- [ ] Repo-wide hygiene gates run at round close (T21.3.5).
- [ ] At least one hardware probe executed OR Phase 4 explicitly deferred
      with rationale.

## 7. Minimal Viable TODO21

1. T21.1.1–T21.1.4 (publication track end to end).
2. T21.2.1 (B-H3 closure).
3. T21.3.1 (ActivityValue) + T21.3A.1–3 + T21.3A.7–8 (dedupe + boundary
   decisions) + T21.3.5 (repo-wide gate once).
4. T21.3A.9 sqlite-toolkit: at least the first store migration with parity
   lock, or an explicit deferral.
Everything else documents deferral in §12.

## 8. Risks

| Risk | Mitigation |
|---|---|
| Manuscript drifts into overclaim | banned-phrase test extended to MANUSCRIPT.md; every number needs an evidence id |
| Conditional science re-inflates | conditions in §2 are binding; default is defer |
| Hygiene pass balloons | repo-wide gates run at round close only, never per-commit |
| Hardware probes overreach | simulation-only framing carried from blueprint; quantization is the simulation of hardware, not hardware |

---

## 12. Progress log

(empty — record sessions here per TODO20 §17 conventions: what shipped,
verdicts + evidence ids, gotchas, env notes, registered opportunities,
gate status snapshot)