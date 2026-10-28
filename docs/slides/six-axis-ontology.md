# The 6-Axis Ontology

```
System = Substrate × Geometry × StateDynamics × Plasticity × CreditAssignment × ParameterUpdate
```

Every experiment is a **coordinate**. Change one axis, hold five constant, and the comparison isolates one mechanism instead of confounding six.

| Axis | Symbol | Question it answers | Primitives |
|---|:--:|---|---:|
| Substrate | `S` | physical state space: precision, noise, sparsity | <!-- gen:substrate_count --> |
| Geometry | `G` | topology and routing of computational units | <!-- gen:geometry_count --> |
| Dynamics | `D` | forward evolution and settling — the "forward pass" | <!-- gen:dynamics_count --> |
| Plasticity | `P` | what becomes a dynamical variable inside an episode | <!-- gen:plasticity_count --> |
| Credit | `C` | how error is routed and pseudo-gradients are computed | <!-- gen:credit_count --> |
| Update | `U` | slow, persistent consolidation of parameters | <!-- gen:update_count --> |

<!-- include: diagrams/coordinate.svg -->

`SystemConfig.validate()` whitelists legal combinations, so the compatible region — not the full Cartesian product — is the search space. The decomposition is a design abstraction, not a law of computation: a five-dimensional system is the `P = NullPlasticity` subspace.

<!-- notes -->
Do not oversell the ontology as physics. It earns its keep only if it makes comparisons legal, and that is an engineering claim: validation whitelists what composes.

Point at the highlighted polygon: this is one system. The dotted hexagon is the inner ring at half scale — a reference grid, not a score. The counts in the table are read from the registries at build time; today they total <!-- gen:primitive_total --> available primitives.
<!-- /notes -->
