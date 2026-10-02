# TODO48.md — Trust the Seams

**Supersedes:** the remaining queue of `TODO47.md` (T7, T8, the round-close
items). **TODO47 is frozen and remains the evidence record** — its §0 doctrine,
§6.1 root-cause analysis and ticket history are not repeated here.
**Binding:** `AGENTS.md` in full. **Binding:** this file.

**Goal:** a system whose *seams* are as trustworthy as its pieces. TODO47's
record is unambiguous about where defects lived: not in the ontology, the
store, or the claims — in the places where two registries, two specs, or two
defaults meet. Six of the eleven measured defects (the lr at 1e-5, the
`beta` warning, the seed shift, the diagonal walk, the off-by-one rounds, the
unreproducible record key) were seam defects. This plan makes the seams
either singular (one implementation) or loud (a gate that fails).

---

## 0. What stands in the way

One paragraph per structural problem, each with its evidence:

1. **Shared hyperparameter names with per-axis meanings.** `step_size`, `beta`
   and `momentum` are each declared by two axes (`harvest.by_axis_specs`) and
   the pairs are *different quantities*: update lr vs settle step, contrast
   weight vs energy scale, SGD momentum vs settle momentum. TODO47 §6.1's
   resolve-once patch made step_size correct by preferring the prior-bearing
   spec; `beta` still resolves per axis and warns on every compose
   (`system.py:405`, dynamics 0.001 vs credit 0.5), and `momentum` resolves
   per axis with nobody checking. The split (per-axis names) removes the
   merging machinery entirely — it is the only change that deletes a defect
   class instead of one instance.
2. **Three step-size/prior registries.** `schema/seed_registries.py`
   (schema `PriorSpec`s), `experiment/learning/prior.py` (the runtime
   `PRIORS_REGISTRY` + `register_all_priors`), and per-axis config dataclass
   defaults as `_config_default`'s last resort (`harvest.py:253`). Resolution
   threads override → prior → config default → `Domain.lo`, four hops with
   different semantics. The 1e-5 bug was born here; its fix added a
   preference rule inside `active()` that is a patch, not a design.
3. **The multiplier table is unmeasured.** `prior.py:96` —
   `("energy_minimization", "thermodynamic_contrast"): 0.00005` — an lr
   prior-center 0.0316 × 5e-5 = 1.6e-6. That cell cannot learn, by
   construction, and the campaign compares credit rules *through* this table.
   Nobody has measured whether any of its 28 rows reflects reality.
4. **Dead defaults inherited from elsewhere.** `max_steps=1` is the harvest
   default for `energy_minimization` — a settling dynamic that settles once.
   The `beta` mismatch warning fires on every legal compose and nobody has
   answered it. Both are the lr bug's shape: a default calibrated for one
   primitive silently inherited by another.
5. **The lab is large and underexercised.** ~12k lines; the T6 fold locked the
   measurement boundary but did not shrink the surface. The retirement
   question (R78) was answered for one function, not for the package.
6. **Locks of unproven fidelity.** TODO47 §1.4's rule exists; the pre-TODO47
   locks have not been audited against "can this fail on the defect it
   names", and two known vacuous shapes (D25, capabilities-are-active) took
   sessions to unmask. `test_wp11_surface_lock.py` (217 s, flaky) still
   prices the property shard.

---

## 1. Rules carried forward

`AGENTS.md`'s Testing section already binds all of TODO47 §1 (select by
symbol, `-rf --tb=line` to a log, killed runs yield no verdict, a lock's
fixture must contain its case, one shard per round close). Nothing new is
added; everything below is executed under those five rules.

---

## 2. The queue

Ordered by *deliverable*, not by interest. Each ticket names its gate. No
ticket's gate is a whole shard.

### Q1 — Does any credit rule separate? The campaign, re-run on a working lr
- **Does:** run the T5 campaign (`examples/learning-rules-and-geometry-digits.yaml`)
  with the lr fix landed and read what it says about credit rules. This is the
  system's purpose and it has never been measured under a working learning
  rate. Report the per-credit accuracy table, not a verdict.
- **Blocks on nothing. Unblocks:** whether Q3's multiplier audit is measured
  or speculative, and whether gate 2 can be strengthened.
- **Gate:** strengthen `test_campaign_lock.py` gate 2: the `gradient`
  reference cell beats 1.5× chance at the campaign's own epochs/batch_limit
  (measured: 0.49 vs chance 0.1 at prior-center lr, 10 epochs — the lock may
  use a cheaper cell but the property must be the reference cell's, not a
  fabricated one). Falsifiable: revert the lr fix, gate goes red.
- **Sub-ticket Q1b (same session if the table is flat):** audit the multiplier
  table (`prior.py:88-121`): for each (dynamics, credit) row, one 10-epoch
  probe at prior-center lr; any row whose effective lr cannot move the loss
  gets its multiplier re-registered with the measurement in the description
  or retired. A row is a prior, not a verdict.

### Q2 — The promotion stage (TODO47 T7, D-a default (i))
- **Does:** a promotion stage writing `status.maturity`: eligibility `L1`
  when a cell achieves `spec.n_seeds` seeds at its declared fidelity with a
  `PASS` gate; promotion `L2` written by the same stage when the eligible
  cell's claim survives re-derivation. `promoted`, `filter_promoted` and the
  report's promotion-history section become measurements.
- **Gate:** a lock asserting a promoted cell reaches `L2` and appears in
  `promotion_history`, on a *measured* store (the lr fix makes real runs
  eligible); the report's `Promoted:` count non-zero on the same run (tier 1).
- **Price:** stage + lock; the stage list already reserves S10 for promotion
  predicates (`stage.py:13`).

### Q3 — Split the shared names; delete the merging machinery
- **Does:** per-axis hyperparameters at the schema level:
  `update_lr` (update axis, Euclid-semantic: per-element displacement), 
  `settle_step` (dynamics axis, per-iteration), `settle_beta`/`contrast_beta`
  (or a single interaction-checked `beta` only where the meanings genuinely
  couple — EqProp's β-matching), `update_momentum`/`settle_momentum`. Delete
  the same-name merging in `active()` and the declare() agreement check they
  existed to guard. The compose-time `apply_dynamics_step_size` /
  `_apply_step_size_overrides` pipeline is then the *only* place the two
  meanings meet, and it names them explicitly.
- **Backwards compatibility: none** (AGENTS.md). Update the T5 campaign YAML,
  the harvest locks, and every spec producer in the same commit.
- **Gate:** (i) no hyperparameter name is declared by two axes — a lock that
  walks `by_axis_specs`; (ii) the reference cell composes with **zero
  warnings**; (iii) the campaign lock from Q1 stays green; (iv) falsifiable:
  re-introduce a shared name, lock (i) goes red.

### Q4 — One prior registry, one resolution function
- **Does:** consolidate `schema/seed_registries.py`'s schema priors and
  `learning/prior.py`'s runtime registry into one `PRIORS_REGISTRY` with one
  accessor (`prior_value`) and one registration path. `_resolve_value`
  shrinks to override → prior → config default, and `Domain.lo` as a
  fallback is deleted (a value with no prior and no config default is a
  schema error at declaration time, not a silent lower bound).
- **Gate:** exactly one `PRIORS_REGISTRY` definition in the repo (grep lock);
  `_config_default` cannot return a `Domain.lo` value for a continuous
  hyperparameter — covered by extending
  `test_a_name_declared_by_two_axes_resolves_once_through_its_prior`'s
  file; the campaign lock stays green.

### Q5 — Defaults audit: no warning fires on a legal compose
- **Does:** for every warning emitted during `compose_configs` + `fit` on the
  reference cell (known: the `beta` mismatch at `system.py:405`; suspect:
  `max_steps=1` on settling dynamics), either fix the default that caused it
  or convert the warning into a validation error so an illegal combination
  fails at compose time. The rule: **a legal cell's compose is silent**.
- **Gate:** a lock that composes every legal cell of the campaign YAML under
  `warnings.error` and asserts none raised (tier 1, priced with `--co` first).

### Q6 — The lab: a census, then retirements
- **Does:** a usage census over `packages/computronium-lab/src`
  (importers, test callers, kernel-path reachability), recorded in
  `packages/computronium-lab/USAGE.md`; every module with no caller and no
  kernel-path reachability gets a retirement record (R78) and deletion.
  Survivors: the facade (`lab.py`), training certificates, synthesis
  (labelled predicted), the ψ-adaptation evaluator (scoped measurement).
- **Gate:** a lock asserting every surviving lab module has an importer
  outside itself; the retirement records live in the census file, one line
  each with the reason. **Decision D-f below sets the census criteria.**

### Q7 — Lock fidelity audit
- **Does:** for every test file under `tests/property/` and
  `tests/acceptance/`, one mutation per lock's named mechanism (remove the
  call, flip the flag, break the invariant) and record green/red in the file's
  docstring or a `LOCK_AUDIT.md`. A lock that stays green with its mechanism
  removed is deleted or rewritten in the same commit (TODO47 §1.4).
- **Also:** split `test_wp11_surface_lock.py` (217 s, two runs failed
  differently — TODO47 §5) so no file exceeds ~60 s.
- **Gate:** the audit table exists and has no "stayed green" rows; wp11's
  replacement files each < 60 s.
- **Note:** this is deliberately *not* mutation testing of everything — one
  mutation per named mechanism, guided by the lock's own docstring.

### Q8 — The small ones (any order)
- **conformance.py reports** an `UNVERIFIED` row's recorded reason instead of
  running it; `codegen.generate_conformance_stubs` stops emitting stubs for
  the 19 unverified rows (TODO47 T8, unchanged).
- **Per-cell `compute_replay_hash` retirement** (TODO47 §5): the run-level
  hash is the gate; retire the unused per-cell API with a record.
- **`comp status --run-id` and the report surface:** promote the §6.1 probe's
  effective-lr printout (`update.step_size` as composed) into
  `ComposedCell.params` reporting so "what lr did this cell train at" is
  answerable from a record without a probe.
- **README archaeology** (low, TODO47 T8).

### Deliberately not in the queue
- New defect archaeology (TODO46 §1 remains its home). A defect that blocks a
  ticket above is pulled forward explicitly; the rest wait.
- `pytest tests/` — never.

---

## 3. Decisions needed from the operator

Three forks; defaults keep the queue unblocked:

- **D-e — split the shared names?** (Q3.) Options: (i) per-axis names as
  proposed; (ii) one name per axis with per-axis config defaults only.
  *Session default:* (i), because it deletes the merging machinery and makes
  the campaign YAML name what it means.
- **D-f — the lab census criteria.** (Q6.) Options: (i) retirement = no
  importer outside the lab and no test exercising it; (ii) retirement = no
  kernel-path reachability *or* demo/recipe use. *Session default:* (i),
  stricter, with (ii) applied to `synthesis/` and `adaptation.py` which the
  T6 locks already scope.
- **D-g — gate 2's strength.** (Q1.) Options: (i) reference cell beats 1.5×
  chance; (ii) measured variation only, retained. *Session default:* (i) —
  the lr fix made it measurable; if the campaign's real cells are too slow,
  the lock prices a cheaper reference cell rather than weakening the
  property.

---

## 4. How a session runs a ticket

Unchanged from TODO47 §4: read this file and `AGENTS.md`; grep for the
touched symbols in `tests/` and run the 2–4 files that name them; implement;
`ruff format` + `ruff check` + `pyright` on changed files; run the ticket's
gate; update this file's ticket with the measured seconds; commit; stop.
Landed tickets leave the queue — the file should get shorter.

## 5. Session log

- (empty — this file is the queue; landed tickets leave it shorter)

---

**The path beyond Q8 is `TODO49.md`** — Phases D–F (device as a schedule
field, campaign economics, long-campaign survival, uncertainty, significance,
contrast design, L2 by replay, CLI/docs/CI/versioning). Its Phase A–C are
this file's queue, unchanged.
