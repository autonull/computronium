## The read: the engine check did its job — my hypotheses didn't survive it

This is a **successful diagnostic, not a failed program.** The entire point of the 10-minute battery was to separate *engineering bugs* from *structural dead ends* before scaling. It did exactly that, and it falsified the specific predictions I handed you. I'll own that cleanly:

- **My P1 hypothesis ("normalization fixes depth") was wrong.** Normalization repaired *magnitude* (hidden norms 2.1e-1..3.2e+1 vs 3.5e-10..5.6e-4 — that sub-result is genuinely green) but cannot repair an **exactly-zero** layer. rms × 0 = 0. The depth wall is channel *structure*, not gain.
- **My P2 hypothesis ("magnitude is broken, direction is fine") was wrong — and backwards.** Direction is the problem. LocalAdam fixed magnitude and PEPITA still sat at chance (0.489–0.507) at every width. Worse, learned-B (0.107) underperformed fixed-B (0.306/0.214) — training B actively hurt. The family is boundary-locked and I'd respect that lock.
- **My P3 hypothesis was half-right:** θ bitwise-invariance is solid (the hard part), but the ψ-step has no supervised term (the tractable part).

The two-pass recheck and the attribution corrections make me *more* confident in the triple-red, not less. This is the CEEC negative-results culture working as designed.

## One mechanism, three manifestations

All three reds reduce to a single statement: **the credit channel is the bottleneck — and you've been patching the signal instead of redesigning the channel.**

| Probe | Root cause | Class | Disposition |
|---|---|---|---|
| **P1 Depth** | 5-step settle can't propagate credit 20 layers → input-weight credit is exactly zero | **Structural** (settling horizon < depth) | Fix via *channel redesign* — architecture |
| **P2 Width** | Fixed random B is directionally uncorrelated; learned-B also fails | **Dead end** (family closed) | **Do not pursue further** |
| **P3 P-Axis** | ψ-step consumes no loss/target term | **Engineering** | Tractable — add supervised term |

The asymmetry is the strategy: **P2 is a closed door, P3 is an engineering fix, P1 demands architecture.** Two of three are not "local learning is dead" — they're "the channel must be co-designed."

## The strategic convergence (this is not a desperate pivot)

The decision matrix prescribed **Architecture Co-Design** on 🔴🔴🔴. Your record confirms that path is **already measured positive in-repo** — the D14 faithful regime and the μPC residual regime both train depth 20+. So this is *convergence onto a live path*, not retreat.

And it's the most Computronium-ian outcome possible: residual/error-bus credit paths are **still local** (each layer's credit route is local; no global transpose, no stored-activation backward sweep). Co-designing the geometry so locality works *is* the thesis. You're not abandoning the substrate story — you're arriving at it. The credit-rule patches were the detour.

## Engine Check Round 2 — the three live levers

Same discipline: ~15 s CPU, zero governance, green/red per probe. Build on what the record says is already production-ready (`credit_norm`, `LocalAdamUpdate`, the frozen-θ ψ harness).

### R2-Probe 1: Residual Co-Design Depth Arm *(tests the pivot — the headline)*
**Action:** Port the D14 faithful composition onto the tiny parity harness — residual geometry (skip paths give credit a shortcut to layer 1) + μPC per-layer init + Adam. Depth sweep 4/8/12/20.
- **🟢 GREEN:** depth-20 parity learns (>chance). → Architecture co-design is the depth fix; the pivot is validated; escalate to the error-bus rung.
- **🔴 RED:** still chance. → Residuals insufficient; the channel needs an *explicit* error bus, or the problem is deeper than topology.

### R2-Probe 2: Supervised ψ Term *(tests the tractable P-axis fix)*
**Action:** Give the plasticity law's `step` a supervised/loss term reading the target from `CompositeState.activity["y"]` (the B5-adjacent lever). Same L3.5 harness, θ frozen (SHA-256 audited), ψ-only 50 steps on Task B.
- **🟢 GREEN:** ψ solves Task B >95% with θ bitwise-invariant. → P-axis is viable; the missing-supervised-term was the *whole* problem. Z3 and continual-learning claims are back on track.
- **🔴 RED:** still fails. → ψ adaptation is structurally broken beyond supervision. Halt Z3; audit the ψ-step contract and `CoupledTransition` timescale isolation.

### R2-Probe 3: Credit SNR — Trapped vs. Noisy *(the diagnostic that decides the next lever)*
**Action:** Build the directional-SNR readout (signal variance vs noise floor per layer); run it on the depth-20 settle path, normalized and unnormalized.
- **Trapped (SNR≈0 at layer 1):** signal never arrives → architecture co-design is *mandatory*; closes the door on any normalization-style rescue.
- **Noisy (SNR>0 but low):** signal arrives but is buried → a denoising/averaging lever could still work; *reopens* the normalization thread.

This probe doesn't just measure — it tells you which of the next two levers is even worth pulling.

## What this means for the agenda

Reweight immediately:
- **Promote** architecture co-design (R2-Probe 1) and the supervised-ψ fix (R2-Probe 2) to the spine — these are the live paths.
- **Deprioritize** the credit-normalization and learned-B threads — the engine check just boundary-locked them at the probe level.
- **Keep** the engine-check script as the standing instrument: a triple-red in 15 seconds is worth more than a month of campaign compute.



---

## EXECUTION RECORD (2026-09-14)

Round 2 implemented and run: `scripts/probes/todo26c_round2.py`
(~19 s CPU, walltime printed never recorded).

### Results

| Probe | Verdict | Evidence |
|---|---|---|
| R2-P1 Residual Co-Design Depth | 🟢 **GREEN** | Depth-20 sign-of-mean 2×2 ablation: residual+μPC **0.865**; residual+default 0.536; μPC-only 0.489; neither 0.496. Depth 4: all arms 0.80–0.89. Only the joint composition trains at depth 20. |
| R2-P2 Supervised ψ | 🟢 mechanism / bar unmet | B 0.676 → **0.734** (+0.058) in 50 steps, θ SHA-256 bitwise invariant, A retained 0.844. The >95% bar needs more episodes/capacity (X-TPC-001: 0.754–0.777 at 600 ep), not a mechanism change. |
| R2-P3 Credit SNR | **Trapped** | Split-half cosine of per-weight credit: layers 19–21 cos **1.000**, layer 10 cos 0.97, layers 1–2 cos **0.000** (norm ~1e-9). rms lifts layer-1 noise 1e-9 → 1.6e-1 with cosine still 0.000 — denoising lever closed. |

### What the round established
1. **The depth wall is an architecture problem, solved in-round.** Residual
   skip paths give the credit a route to layer 1 AND μPC depth-scaled init
   keeps the channel conditioned; *neither alone suffices* (clean 2×2). This
   is the TODO26b decision matrix's prescribed pivot, now measured green at
   the probe level with ePC credit and LocalAdam — no Muon.
2. **The TODO26b P2 "optimizer crutch" reading is revised:** with co-designed
   geometry, a cheap substrate-native local optimizer (LocalAdam) is
   sufficient. The crutch was compensating for geometry, not credit
   direction.
3. **Supervised ψ works** — the P-axis lever TODO26b flagged is confirmed
   tractable on this exact harness (and by X-TPC-001/002 at governed scale).
4. **The normalization/learned-B threads stay closed** — R2-P3's SNR
   instrument shows why: the input-side channel carries zero coherent
   signal, and normalization amplifies the noise floor incoherently.

### Defect found & fixed (library)
- `computronium/ontology/geometry.py:642` (`_apply_stack`): residual skip
  used in-place `h += h_in`, breaking the autograd graph for
  residual+BackpropCredit training (RuntimeError: modified in-place). The
  sibling `route()` method already used the out-of-place form with the
  explanatory comment — the fix applies the same convention. Targeted tests
  (`test_residual_geometry.py` + wiring lock, 10 passed) green.

### Harness lesson
- 16-bit parity at the 60-batch budget exceeds **exact backprop** (residual
  +μPC+BP control: chance at depth 4 with 4× budget). The parity arm can
  never certify an accuracy axis. Engine checks must use BP-learnable tasks
  (sign-of-mean reaches 0.979 with BP) so red verdicts are attributable to
  the arm, not the ruler.

### Method note (honesty ledger)
R2-P3's first draft measured raw settle ε with reversed layer indexing and
showed an illusory "cos 0.404 at layer 1". The corrected instrument
(per-weight contrastive credit, true indexing) shows the trap. The verdict
in the probe docstring records the correction.

### New improvement opportunities
- **Error-bus rung**: R2-P1's residual shortcut works; the explicit error
  bus (per-layer prediction targets, w0 family) is the next rung — does it
  beat residuals at depth 20+ on the fair task?
- **ψ at the 0.95 bar**: supervised ψ acquisition is real; scale episodes
  (600+) or ψ capacity on this switch to see whether 0.95 is reachable
  before claiming the Z3 flagship.
- **Multi-seed + MNIST confirmation** of the R2-P1 green (single seed,
  quick budget here — the μPC residual regime probes already carry the
  MNIST-depth evidence; a 3-seed sign-of-mean repeat is cheap).
