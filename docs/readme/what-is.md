## What is Computronium

Computronium ships three layers, each usable independently. This is the single
capability inventory; the primitive lists live once under
[the 6-axis ontology](#the-6-axis-ontology), and what is designed rather than
built lives in the [readiness ledger](#what-is-proven-what-is-designed-and-what-is-not).

| Layer | What it is | What you get |
|---|---|---|
| **ML library** (`computronium` core) | Composable 6-axis learning systems behind one training API | Any coordinate of Substrate × Geometry × StateDynamics × Plasticity × CreditAssignment × ParameterUpdate (5-D systems are `P = NullPlasticity`); Backprop, EqProp, FA, DFA, Forward-Forward, PEPITA, Target Prop, Predictive Coding, Hebbian/STDP, SNN, TileNet and 6-D joint rules under one `SystemTrainer`; digital, memristive, neuromorphic, photonic and quantum substrates; spectral-radius, Lyapunov, settling-time, basin-stability and free-energy analysis; frozen-θ ψ lifecycles and a credit-swap demo |
| **Experiment kernel** (`computronium.experiment`) | Question → `RunSpec` → policy → pipeline → evidence store → claims | Reproducible, resumable, policy-interchangeable runs over <!-- gen:stage_count --> stages and <!-- gen:policy_count --> proposal policies; <!-- gen:objective_count --> objectives (<!-- gen:measured_objective_count --> measured) with multi-objective Pareto promotion; a single DuckDB evidence store with fail-closed schema versioning; statistical promotion, claims, limitations and per-stage timings |
| **Scientific program** (hypotheses + governance) | Motivating hypotheses on locality, plasticity, stability and physical constraints; standalone CEEC governance ledger | Labeled empirical investigation — every claim carries a verification level; a fairness contract, pre-registered thresholds, generated identity cards, a corrections log, and three findings that survived audit ([Findings we own](#findings-we-own)). The motivating hypothesis is an *agenda*, not a result |

**Claim-strength discipline.** Every claim in this README is labeled by its verification level: (1) analytical, (2) machine-checked, (3) certified numerical, (4) sampled numerical, (5) empirical. Levels are defined in `computronium.verification` and enforced against banned overclaim phrases.
