# The Crisis of Comparison

Three failure modes, and one thing they have in common: the comparison is not the artifact.

- **Unequal tuning budgets.** A published advantage is often a better hyperparameter sweep, not a better learning rule.
- **Unverified code.** Every paper re-derives its baseline; a re-implementation defect reads as an algorithmic result.
- **The metric trap.** One scalar hides the dynamics — stability, energy, memory, and plastic-state capacity trade against accuracy.

**What is missing is not another algorithm. It is a fair way to compare them.**

| Artifact of the comparison | What it silently encodes |
|---|---|
| architecture and width | inductive bias |
| seed count and selection rule | variance budget |
| hyperparameter prior | the author's tuning effort |
| the reported metric | which trade-off is allowed to hide |

<!-- notes -->
Frame this as infrastructure, not accusation: individual papers are usually careful, the field has no shared instrument.

Walk the table left to right. Each row is a degree of freedom a comparison must declare before it is legal. The fairness contract in the closing slide is the answer to this table, clause by clause.
<!-- /notes -->
