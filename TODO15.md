# TODO15.md — The 60-Minute Sprint: Diagnostics First, Verdicts Second

> **Opened 2026-09-09.**
>
> **Constraint:** Time is strictly limited. No multi-hour design sessions.
> No proactive infrastructure. No long-run training cells without a
> ≤5-minute diagnostic proving they are necessary.
>
> **Doctrine:** *Measure before building. Autopsy before training.*
> Every hypothesis gets a ≤5-minute pure-tensor diagnostic on existing
> frozen weights. If the diagnostic is decisive, we skip training and
> write the boundary. If ambiguous, we train the minimal discriminating cell.
>
> **Ratchet policy:** REACTIVE ONLY. We lock defects we encounter.
> We do not write locks for hypothetical bugs.

---

## §1 — Phase 1: Diagnostic Triage (00:00–00:12, No Training)

### 1.1 The ψ-Variance Oracle (replaces the piecewise-ψ design session)

**Question:** §24 D1 failed because a single linear ψ can't average over
ReLU mask diversity. Does mask-conditioning actually resolve the target,
or is within-mask variance too high for any affine correction?

**The 3-minute test (pure tensor math on the frozen D1 backbone):**
1. Load the §24 D1 scale backbone (784→128⁴→10, θ SHA-locked).
2. Pass 1,000 FashionMNIST images. Record the ReLU mask at layer 2.
3. Compute exact mask-aware Jacobian targets T_s = R @ pinv(J_s) per image.
4. Cluster masks by exact pattern (hash). For the top-3 clusters by frequency:
   - Within-cluster variance: Var(T_s | mask = m)
   - Across-cluster variance: Var(E[T_s | mask = m]) across m
   - Condition number: cond(G_m + λI) for the dominant cluster

**Verdict (pre-registered):**
- Within ≪ Across AND cond < 1e6 → **GO: piecewise-ψ is mathematically
  validated.** Proceed to §2.2.
- Within ≈ Across → **NO-GO: mask pattern doesn't resolve the target.
  Flagship B at scale is permanently closed.** Write the boundary.
- Within ≪ Across BUT cond > 1e6 → **AMBIGUOUS: target is separable but
  the solve is ill-conditioned.** Needs regularization redesign (not a
  20-min cell). Defer piecewise-ψ; pivot to Depth-50.

**Stop-loss:** if NO-GO, do NOT build piecewise-ψ. The 20-minute Phase 2
block goes entirely to the Depth-50 rescue.

### 1.2 The Depth-50 Autopsy (replaces the 60-minute budget sweep)

**Question:** Is the depth-50 collapse (0.397 at 150 batches) an
initialization failure, an optimization failure, or a data-budget failure?

**The 3-minute test (10 batches, no verdict run):**
1. Instantiate depth-50 (784→128×50→10). Run exactly 10 batches.
2. Measure on the FIRST forward pass: activation ratio ‖a_50‖/‖a_1‖.
3. Measure on the FIRST backward pass: gradient ratio ‖g_1‖/‖g_50‖.
4. Measure loss velocity: (L_1 − L_10) / L_1.
5. At batch 50 (if reached in <2 min): Train Acc vs Val Acc.

**Verdict (pre-registered):**
- Activation or gradient ratio < 0.01 or > 100 → **Init/vanishing failure.**
  Fix: μPC init rescale. Run 150-batch cell with fix. (~10 min)
- Loss velocity < 1% AND gradients healthy → **Optimizer/LR failure.**
  Fix: screen Muon 0.02 vs OrthoAdam 0.01. Run 150-batch cell. (~10 min)
- Train ≫ Val at batch 50 → **Memorization/capacity failure.**
  Fix: add weight decay 1e-3 or dropout 0.1. Run 150-batch cell. (~10 min)
- All healthy, loss descending, Train ≈ Val → **Data-budget limited.**
  The 150-batch budget is simply too small for 50 layers. Run 300-batch
  cell ONLY if time permits. Otherwise: boundary (data-limited, not
  dynamical). Write it.

---

## §2 — Phase 2: Execution Block (00:12–00:50, Gated by Phase 1)

### 2.1 W7 Muon Blitz (12 minutes, parallel)

**Pre-requisite:** OMP_NUM_THREADS=2 per process (the §11.11 thrash lesson).

| Cell | Code | Est. | Pre-registered rescue | Pre-registered boundary |
|------|------|------|-----------------------|-------------------------|
| PEPITA × Muon 0.02 | Existing probe | ~3 min | ≥ 0.65 → Reopened | < 0.40 → Boundary |
| Frozen-Error × Muon 0.02 | Existing probe | ~3 min | ≥ 0.65 → Reopened | < 0.40 → Boundary |
| STDP × Muon 0.02 (plain, no modulation) | Existing probe | ~3 min | ≥ 0.50 → Reopened | < 0.30 → Boundary |

**Note:** STDP + reward modulation (W7.3b) requires new code. It is
DEFERRED unless plain STDP × Muon fails AND spare time exists.

**Promotion gate for any positive:** 3-seed confirmation is DEFERRED to
a follow-up session. A single-seed rescue ≥ threshold is recorded as
**Reopened (seed 0)** — sufficient to change the status and queue the
promotion round, but not sufficient for a headline.

### 2.2 Targeted Rescue (25 minutes, ONE path only)

**Execute ONLY the path justified by Phase 1. Hard fork:**

**If §1.1 = GO (piecewise-ψ validated):**
- Implement minimal piecewise-ψ: k = top-2 clusters by frequency
  (no K-means, no design session — just the two most common masks).
- Key: exact bitmask hash (md5 of the byte tensor, 8 chars).
- Solve: one ridge per cluster, applied at inference by mask lookup.
- Run: seed 0 only, §24 D1 cell (784→128⁴→10, MNIST→FashionMNIST).
- Overturn criterion: hidden ψ > readout ceiling (0.674) by ≥ +0.02.
- If seed 0 passes: queue 3-seed round for next session. Record as
  **Reopened (seed 0, pending promotion).**
- If seed 0 fails: run §17 defect audit (5 min). If no defect found:
  **Boundary at scale, permanent.**

**If §1.1 = NO-GO or AMBIGUOUS:**
- Skip piecewise-ψ entirely.
- Execute the §1.2 fix (init rescale / optimizer screen / regularization)
  as a 150-batch depth-50 cell. (~10 min)
- If the fix works (test acc ≥ 0.75): **§22 #4 met.** Queue 3-seed.
- If the fix fails: **Depth-50 boundary, classified.** Write it with the
  specific limiting factor from §1.2.

---

## §3 — Phase 3: Reactive Ratchet (00:50–00:60)

**Rule:** We lock ONLY what we encountered.

1. If any Phase 2 cell hit a silent defect (inert channel, byte-identical
   arms, frozen weights): write the 5-line assertion that catches it,
   paste it into the probe, move on. No library-level refactoring.
2. If no defects encountered: no ratchet work. The sprint ends.
3. Write the TODO15 verdict log (4 sentences max per workstream).

---

## §4 — Explicit Kills (time bought)

| Killed | Reason |
|--------|--------|
| W0 longer-context | Mechanism mapped; scale test yields no new capability |
| W8.6 (NCA+NTM moonshot) | Breadth sufficient; consolidation needed |
| Per-site FA primitive (lattice) | Requires invention; we only have time for execution |
| Proactive Register D locks | Reactive only; hypothetical bugs don't burn sprint time |
| 3-seed promotion rounds (this sprint) | Deferred to follow-up; single-seed reopen is sufficient to change status |
| STDP + reward modulation (W7.3b) | Requires new code; plain STDP × Muon is the cheaper first rung |

---

## §5 — Timeline

| Min | Action | Gate |
|-----|--------|------|
| 00–03 | ψ-Variance Oracle (§1.1) | GO / NO-GO / AMBIGUOUS |
| 03–06 | Depth-50 Autopsy (§1.2) | Failure-mode classification |
| 06–08 | Write W7 Blitz probe commands | — |
| 08–20 | W7 Muon Blitz (3 cells, parallel) | 3 verdicts |
| 20–22 | Analyze Phase 1 + W7. Pick ONE §2.2 path. | Fork decision |
| 22–47 | Targeted Rescue (§2.2) | Flagship B verdict OR §22 #4 |
| 47–55 | §17 audit if needed; reactive ratchet | — |
| 55–60 | Write verdict log. Lock repo state. | Sprint closed |

---

## §6 — Stop-Loss Conditions (hard)

1. ψ-Oracle NO-GO → Flagship B at scale is DEAD. Do not build piecewise-ψ.
2. Depth-50 autopsy shows healthy dynamics BUT 150-batch Muon fails →
   Depth-50 is a data-budget boundary. Do NOT escalate to 600/1200.
3. W7 Blitz: all three cells < 0.40 → the I(C,U) thesis has limits.
   Record as boundaries. Do not theorize. Move to §2.2.
4. If BOTH §2.2 paths fail: the sprint ends at minute 50. Write the
   boundaries. The project's state is honest and the queue is clear.

---

## §7 — What This Sprint Does NOT Do

- It does not expand the ontology.
- It does not run AutoScientist campaigns.
- It does not touch the gallery or demo infrastructure.
- It does not write new credit primitives.
- It does not run any cell longer than 25 minutes.
- It does not pre-register predictions it cannot test in the time budget.

The sprint produces at most THREE new status changes (from the Overturn
Table) and at most ONE flagship verdict. That is enough.

