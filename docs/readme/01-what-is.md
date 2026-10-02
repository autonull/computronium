## 1. What is Computronium

Computronium ships three layers, each usable independently:

| Layer | What it is | What you get |
|---|---|---|
| **ML Library** (`computronium` core) | Composable 6-axis learning systems behind one training API | Train and compare Backprop, EqProp, FA, FF, PEPITA, Target Prop, Predictive Coding, Hebbian/STDP, SNN, TileNet, and 6-D joint variants under a single `SystemTrainer` interface |
| **Experiment Kernel** (`computronium.experiment`) | Question → RunSpec → policy → pipeline → evidence store → claims | Reproducible, resumable, policy-interchangeable experiments with a single DuckDB evidence store and fail-closed schema versioning |
| **Scientific Program** (hypotheses + governance) | Motivating hypotheses on locality, plasticity, stability, and physical constraints; CEEC epistemic governance | Ongoing empirical investigation — claims below are labeled by verification level, never asserted beyond their evidence |

**Claim-strength discipline.** Every claim in this README is labeled by its verification level: (1) analytical, (2) machine-checked, (3) certified numerical, (4) sampled numerical, (5) empirical. Levels are defined in `computronium.verification` and enforced against banned overclaim phrases. The motivating hypothesis — that learning systems native to physical constraints (asynchrony, locality, limited precision, energy budgets) offer measurable benefits — is an *agenda*, not a result.

---
