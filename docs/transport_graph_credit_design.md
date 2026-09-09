# §6.2 Design: Minimal Transport-Graph Credit Rule

**Status:** design only (per TODO16 §6.2 — no implementation until the §6.1
grid shows the transport graph is the binding constraint). Zero compute.

**Trigger for implementation:** the §6.1 reduced grid
(`scripts/probes/w16_transport_grid.py`) must show at least one fixed-write
memory type failing recall (< 0.85) while a learned-addressing type succeeds.
Measured so far (2026-09-09): slot-capped fixed writes hit 1.000 on
explicit-key recall in 300 steps, and the recorded sparse-addressed NTM
local3 sits at 0.625–0.646 acc_given_hit — the OPPOSITE ordering. Fixed
writes dominate; learned addressing is the deficit. Under that ordering this
primitive is NOT the binding constraint and stays unimplemented.

## Motivation

§5.4 verdict: NTM recall failure is pure value binding under zero-history
factorization (acc_given_hit 0.63 with read hit-rate 1.0 by construction).
The missing credit is the gradient path *through the memory tensor*: the
writer emits content whose usefulness is only observable at a later cued
read, and no per-module local loss spans write→read.

## Proposed primitive: `TransportGraphCredit(CreditAssignment)`

A local rule that supervises the writer against the reader's *actual
consumption*, without backpropagating across timesteps:

1. **Consumption capture.** At each cued read, record the read vector
   `r_t` and the reader's post-activity. The read is causally attributable
   to a specific write (explicit keys make the slot→write mapping exact;
   soft addressing keeps a per-slot responsibility weight `a_w`).
2. **Writer target = reader error transport.** At the cued read, the
   output CE w.r.t. `r_t` defines a desired read change `δr`. Under
   `r = a_r · mem`, the per-slot desired content change is
   `δc_s = δr_s / a_r,s` (guarded for small attention). The writer's local
   loss is `||add_v_t − (c_t + γ·δc_{read(t)})||²` — i.e. the write target
   is corrected by what the reader later needed. This is a two-phase,
   *delayed-local* rule: one episode of bookkeeping, no cross-timestep
   autograd graph.
3. **Parameterization.** Only the writer projections `kw/add/erase` and
   read `kr/beta` receive these losses; the controller keeps its ordinary
   step-CE. Zero history: every loss input detached at the timestep
   boundary (same discipline as the `local3` arms).

## Why this is the minimal move

- It adds no new ontology primitive: it composes the existing writer
  surrogates (`_writer_target`, expected-content MSE) with a read-side
  error signal already computed at cued reads.
- It is falsifiable at probe scale: rerun `w8_ntm_copy --arm=local3` with
  the transport term; pre-register acc_given_hit 0.63 → ≥ 0.85.
  Falsification ⇒ value binding needs recurrent state (history), closing
  the zero-history family entirely on retrieval tasks.

## Standing precondition

Implementation is blocked until (a) §6.1 is complete and (b) the user
confirms a new credit-rule composition is wanted (Execution Rule 8: no new
primitives without Phase 2 survival + user confirmation). Given the current
fixed-write dominance, the expected §17 law is: **on explicit-key retrieval
tasks the binding constraint is the learned-addressing machinery, not the
gradient path through memory** — in which case the correct lever is simpler
fixed-write transport graphs, not richer credit.
