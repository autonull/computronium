# ceec-core

Standalone epistemic governance ledger — evidence, beliefs, gates, quarantine,
calibration, and audit — extracted from the Computronium project (CEEC-Core
v1.0 semantics). No Computronium dependency.

## What it does

CEEC-Core is an append-only SQLite ledger for rigorous ML experimentation.
It records artifacts, evidence, beliefs, goals, experiments, and decisions;
enforces promotion/boundary/quarantine gates; tracks calibration; and audits
the ledger for epistemic defects.

## Install

```bash
pip install -e packages/ceec-core
ceec init --ledger-dir ./ledger
ceec audit --ledger-dir ./ledger
```

## Usage

```python
from ceec import CEECStore, models
from ceec.audit import run_audit

with CEECStore("ledger/ceec.sqlite3", "ledger/artifacts") as store:
    artifact = store.ingest_artifact(b"results", "blob")
    scope = models.Scope(domain="credit", credit=("gradient",))
    evidence = store.record_evidence(kind="vector", scope=scope,
        artifact_refs=[artifact.id], axes=["acc"], values_ref=artifact.id)
    findings = run_audit(store)  # [] means clean
```

## Validated scope

CEEC-Core semantics are the ones exercised by the internal Computronium
ledger (single-writer SQLite, quick-budget probes, 2026-09 ledger at 26+
evidence records, audit clean). No concurrent-writer hardening; no network
or multi-process guarantees.

## Known limitations

- Single-process, single-writer SQLite (`_next_id` is not concurrency-safe).
- Hard-constraint validation is a generic interface (`ceec.constraints`);
  project-specific constraints must be supplied by the caller.
- No CLI daemon or server; commands are one-shot.

## Evidence references

Internal ledger: `computronium` repo `ceec/ceec.sqlite3` (E-000001..E-000026);
gate semantics tested in `tests/test_gates.py`; audit checks in
`computronium/ceec/audit.py` (identical extraction).

## Verification level

Unit-tested + quickstart regression; semantics parity with the internal
CEEC enforced by `tests/platform/test_ceec_core_compat.py` in the parent repo.

## Dependencies

Python standard library + `pydantic` (validation at the I/O boundary).
The TODO20 plan nominally specifies stdlib-only; pydantic v2 is a documented
deviation chosen over rewriting validated models.

----

# CEEC and NAL

By rooting CEEC in **NAL (Non-Axiomatic Logic)**—specifically the evidence-tracking and goal-directed mechanics of NARS (Non-Axiomatic Reasoning System)—the design shifts from being just a "database schema" to a formalized **cognitive architecture for an autonomous scientist**.

Here is how the NAL inspiration clarifies CEEC's design and sharply defines the contrast with Agora.

### 1. The NAL Connection: What was kept and what was dropped

In NAL, an intelligent system does not assume it has perfect axioms. Instead, it operates under the *Assumption of Insufficient Knowledge and Resources* (AIKR). It manages its state using:
*   **Beliefs:** Judgments about the world, grounded in accumulated positive and negative evidence, which yields a truth value (frequency and confidence).
*   **Goals:** Desired states that drive the system’s resource allocation and attention.
*   **Term Reasoning:** The formal syllogistic inference rules (deduction, abduction, induction) used to derive new beliefs from old ones.

**CEEC's Adaptation ("Minus Term Reasoning"):**
CEEC strips away the complex symbolic inference engine (the Term Reasoning). Instead of using formal logic to deduce new beliefs, it uses **empirical ML experiments** to generate evidence.
*   It keeps the **Evidence Accumulation** model: Beliefs don't just flip from "false" to "true"; their probability/confidence is continuously updated as positive evidence (promotions) and negative evidence (boundaries/quarantines) are ingested.
*   It keeps the **Goal-Driven Control** model: Goals aren't just metadata; they are the active steering mechanism that dictates which experiments are selected and prioritized.

### 2. The Mapping: NAL Concepts to ML Governance

This mapping explains why CEEC's object model is so strictly typed and why the "Chain" (`Experiment → Artifact → Evidence → Derived → Belief → Status`) exists.

#### A. Beliefs = Experiment Results (Hypotheses with Confidence)
In CEEC, a `Belief` is not a static fact. It is an active hypothesis (e.g., *"Mechanism X improves generalization on Task Y"*).
*   **NAL equivalent:** A judgment with a truth value `<f, c>` (frequency, confidence).
*   **CEEC implementation:** A Belief starts as `open`. As experiments run, they generate `Evidence` (raw metrics, loss curves, parity checks). The `Derived` records act as the evidence integrators—calculating statistics like the "chance-band" or Brier scores. These derived metrics update the Belief's probability. If the accumulated evidence crosses a formal threshold (e.g., $P_{low} \ge 0.95$), the Belief is *promoted* (high confidence). If negative evidence accumulates (rescue probability $\le 0.05$), it is declared a *boundary* (certified dead end).

#### B. Goals = Experiment Goals (The Optimization/Attention Driver)
In CEEC, `Goals` represent the overarching research objectives or optimization targets (e.g., *"Minimize bits-per-byte on the weight-transfer task"* or *"Find a local learning rule that matches backprop"*).
*   **NAL equivalent:** Desire values that dictate which operations the system should perform next to reduce uncertainty or achieve a state.
*   **CEEC implementation:** Goals are not passive tags. They interact with Beliefs to drive the **§22 Experiment Selection** mechanism. When the system decides what to do next, it evaluates candidates based on how much they advance a Goal (`ExpectedValue / Cost`). A Belief that is highly relevant to a high-priority Goal will trigger the pre-registration of new experiments to resolve its uncertainty.

#### C. Evidence = The Update Mechanism
In NAL, evidence is the raw input that shifts belief confidence. In CEEC, the `Artifact → Evidence → Derived` pipeline is the physical instantiation of NAL's evidence accumulation. The system cannot just "decide" a belief is true; it must ingest an `Artifact` (a reproducible run), record the `Evidence` (the metrics), and derive the statistical impact on the `Belief`.



